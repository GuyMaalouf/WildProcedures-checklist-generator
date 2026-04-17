#!/usr/bin/env python3
"""
Drone Operations Checklist Generator
A standalone tool for generating custom drone operation checklists and procedure manuals.

Usage:
    python generate_checklist.py [options]

Example:
    python generate_checklist.py --operation VLOS --drone DJI --count SINGLE
"""

import json
import os
import sys
import shutil
from fpdf import FPDF
from datetime import datetime
import argparse

from profile_utils import create_profile, list_profiles, resolve_data_paths


def load_constants(constants_file=None):
    """Load constants from JSON file."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    if constants_file is None:
        constants_file = os.path.join(script_dir, 'data/constants.json')
    
    if os.path.exists(constants_file):
        with open(constants_file, 'r', encoding='utf-8') as f:
            constants_data = json.load(f)
            return (
                [tuple(x) for x in constants_data['operation_types']],
                [tuple(x) for x in constants_data['drone_platforms']],
                [tuple(x) for x in constants_data['number_of_drones']]
            )
    else:
        # Fallback to defaults if file doesn't exist
        return (
            [('VLOS', 'VLOS'),
             ('BVLOS_NO_VO', 'BVLOS 1km (No Observer)'),
             ('BVLOS_VO', 'BVLOS 2km (Observer)'),
             ('NIGHT_VLOS', 'Night VLOS'),
             ('NIGHT_BVLOS', 'Night BVLOS')],
            [('DJI', 'DJI'),
             ('EBEE', 'Ebee X'),
             ('UOB_GLIDER', 'UoB Glider'),
             ('SMURF', 'Papa Smurf'),
             ('CODRONE', 'CoDrone'),
             ('PARROT', 'Parrot Anafi')],
            [('SINGLE', 'Single Drone'),
             ('MULTIPLE', 'Multiple Drones'),
             ('SWARM', 'Swarm of Drones')]
        )


# Load constants
OPERATION_TYPE_CHOICES, DRONE_PLATFORM_CHOICES, NUMBER_OF_DRONES_CHOICES = load_constants()


def safe_pdf_text(value):
    """Return text that can always be rendered by the built-in FPDF fonts."""
    if value is None:
        return ""
    text = str(value)
    replacements = {
        "\u2014": "-",
        "\u2013": "-",
        "\u2018": "'",
        "\u2019": "'",
        "\u201c": '"',
        "\u201d": '"',
        "\u2022": "-",
    }
    for source, target in replacements.items():
        text = text.replace(source, target)
    return text.encode("ascii", "ignore").decode("ascii")


class ChecklistGenerator:
    """Generator for creating customized drone operation checklists and procedure manuals."""

    def __init__(self, checklist_files, operation_type, drone_platform, number_of_drones):
        """
        Initialize the checklist generator.
        
        Args:
            checklist_files: List of JSON file paths containing checklist data
            operation_type: Type of operation (VLOS, BVLOS, EVLOS)
            drone_platform: Drone platform type (DJI, AUTEL, OTHER)
            number_of_drones: Number of drones (SINGLE, MULTIPLE)
        """
        self.checklist_files = checklist_files
        self.operation_type = operation_type
        self.drone_platform = drone_platform
        self.number_of_drones = number_of_drones
        self.checklists = self.load_checklists()

        # Set up paths for resources (logo only). Core PDF fonts are used so
        # the generator works out of the box without shipping TTF files.
        script_dir = os.path.dirname(os.path.abspath(__file__))
        self.logo_path = os.path.join(script_dir, 'media/WD_logo.png')
        
        # Create output directory if it doesn't exist
        self.output_dir = os.path.join(script_dir, 'output')
        self.archive_dir = os.path.join(self.output_dir, 'archive')
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(self.archive_dir, exist_ok=True)
        
    def archive_existing_pdfs(self):
        """Archive all existing PDF folders in the output directory."""
        if not os.path.exists(self.output_dir):
            return
            
        # Get all items in output directory
        items = os.listdir(self.output_dir)
        
        for item in items:
            item_path = os.path.join(self.output_dir, item)
            # Skip the archive directory itself
            if item == 'archive':
                continue
            # Move folders and PDF files to archive
            if os.path.isdir(item_path) or item.endswith('.pdf'):
                archive_path = os.path.join(self.archive_dir, item)
                # If item already exists in archive, add timestamp
                if os.path.exists(archive_path):
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    base_name = item
                    archive_path = os.path.join(self.archive_dir, f"{base_name}_{timestamp}")
                shutil.move(item_path, archive_path)
                print(f"  Archived: {item} → archive/")
    
    def create_output_folder(self, timestamp):
        """Create a folder for the current PDF generation."""
        folder_name = f"{self.operation_type}_{self.drone_platform}_{self.number_of_drones}_{timestamp}"
        folder_path = os.path.join(self.output_dir, folder_name)
        os.makedirs(folder_path, exist_ok=True)
        return folder_path

    def load_checklists(self):
        """Load checklist data from JSON files."""
        checklists = []
        for file in self.checklist_files:
            if not os.path.exists(file):
                print(f"Warning: File not found: {file}")
                continue
            with open(file, 'r', encoding='utf-8') as f:
                checklists.append(json.load(f))
        return checklists

    def filter_procedures(self, procedures):
        """
        Filter procedures based on operation type, drone platform, and number of drones.
        
        Args:
            procedures: List of procedure dictionaries
            
        Returns:
            List of filtered procedures matching the specified criteria
        """
        filtered_procedures = []
        for procedure in procedures:
            if (self.operation_type in procedure['operation_types'] or 'ALL' in procedure['operation_types']) and \
               (self.drone_platform in procedure['drone_platforms'] or 'ALL' in procedure['drone_platforms']) and \
               (self.number_of_drones in procedure['number_of_drones'] or 'ALL' in procedure['number_of_drones']):
                filtered_procedures.append(procedure)
        return filtered_procedures

    def filter_sections(self, items):
        """Return only sections that contain at least one matching procedure."""
        filtered_sections = []
        for section in items:
            matched_procedures = self.filter_procedures(section.get('procedures', []))
            if not matched_procedures:
                continue
            filtered_sections.append({
                'section': section.get('section', 'Untitled Section'),
                'procedures': matched_procedures,
            })
        return filtered_sections

    def add_branding_banner(self, pdf, title, max_title_width, vertical_spacing):
        """Add logo and title banner to the PDF page."""
        if os.path.exists(self.logo_path):
            pdf.image(self.logo_path, 10, 6, 28)
        pdf.set_font("Helvetica", style='B', size=20)
        combined_title = safe_pdf_text(f"{title}").upper()
        pdf.set_x((pdf.w - max_title_width) / 2)
        pdf.multi_cell(max_title_width, 10, combined_title, align='C')
        pdf.ln(vertical_spacing)

    def add_metadata(self, pdf, font_size, box_width):
        """Add metadata box with operation details and timestamp."""
        pdf.set_font("Helvetica", size=font_size)
        operation_type_expanded = dict(OPERATION_TYPE_CHOICES).get(self.operation_type, self.operation_type)
        drone_platform_expanded = dict(DRONE_PLATFORM_CHOICES).get(self.drone_platform, self.drone_platform)
        number_of_drones_expanded = dict(NUMBER_OF_DRONES_CHOICES).get(self.number_of_drones, self.number_of_drones)
        current_datetime = datetime.now().strftime("%d-%m-%Y %H:%M")
        metadata = safe_pdf_text(
            f"{operation_type_expanded} | {drone_platform_expanded} | {number_of_drones_expanded} | {current_datetime}"
        )
        pdf.set_fill_color(211, 211, 211) 
        pdf.cell(box_width, font_size*0.6, metadata, border=1, ln=True, align='C', fill=True)

    def generate_checklist_pdf(self, output_folder, filename):
        """
        Generate a compact A5 checklist PDF.
        
        Args:
            output_folder: Path to the output folder
            filename: Name of the output PDF file
        """
        ## STYLING
        bullet_spacing = 5
        font_size = 10
        box_width = 120
        vertical_spacing = font_size / 2
        max_title_width = 75
        
        ## Initialize PDF
        pdf = FPDF(format='A5')
        pdf.set_font("Helvetica", size=font_size)
        rendered_any_content = False
        
        for checklist in self.checklists:
            title = checklist['title']
            color = checklist.get('color', [0, 0, 0])
            items = self.filter_sections(checklist.get('items', []))
            if not items:
                continue

            rendered_any_content = True
            page_number = 1
            pdf.add_page()
            
            # Calculate section height
            section_height = vertical_spacing
            for section in items:
                for procedure in section['procedures']:
                    text_width = pdf.get_string_width(safe_pdf_text(procedure['checklist_entry']))
                    lines = max(1, ((text_width+bullet_spacing) // (box_width))+1)
                    section_height += vertical_spacing * lines
            
            # Add header
            if pdf.get_y() + section_height > pdf.h - pdf.b_margin:
                self.add_branding_banner(pdf, f"{title} ({page_number})", max_title_width, vertical_spacing * 1.5)
            else:
                self.add_branding_banner(pdf, f"{title}", max_title_width, vertical_spacing * 1.5)
            
            self.add_metadata(pdf, font_size-3, box_width)
            pdf.set_fill_color(*color)
            pdf.rect(140, 0, 10, 210, 'F')  # Color band on the right for A5
            pdf.set_text_color(0, 0, 0)
            pdf.set_font("Helvetica", size=font_size)
            
            # Process sections
            for section in items:
                section_height = vertical_spacing
                for procedure in section['procedures']:
                    text_width = pdf.get_string_width(safe_pdf_text(procedure['checklist_entry']))
                    lines = max(1, ((text_width+bullet_spacing) // (box_width))+1)
                    section_height += vertical_spacing * lines

                # Check if new page is needed
                if pdf.get_y() + section_height > pdf.h - pdf.b_margin:
                    page_number += 1
                    pdf.add_page()
                    self.add_branding_banner(pdf, f"{title} ({page_number})", max_title_width, vertical_spacing * 1.5)
                    self.add_metadata(pdf, font_size-3, box_width)
                    pdf.set_fill_color(*color)
                    pdf.rect(140, 0, 10, 210, 'F')
                    pdf.set_text_color(0, 0, 0)
                    pdf.set_font("Helvetica", size=font_size)

                # Draw section box
                pdf.rect(10, pdf.get_y(), box_width, section_height, 'D')
                pdf.set_fill_color(*color)
                pdf.rect(10, pdf.get_y(), box_width, vertical_spacing, 'F')
                pdf.set_font("Helvetica", style='B', size=font_size + 2)
                pdf.set_text_color(255, 255, 255)
                pdf.cell(box_width, vertical_spacing, txt=safe_pdf_text(section['section']), ln=True, align='C')
                pdf.set_text_color(0, 0, 0)
                pdf.set_font("Helvetica", size=font_size)
                
                # Add procedures
                for procedure in section['procedures']:
                    text_width = pdf.get_string_width(safe_pdf_text(procedure['checklist_entry']))
                    lines = max(1, text_width // (box_width - bullet_spacing))
                    pdf.cell(bullet_spacing, vertical_spacing * lines, txt='o', ln=False)
                    pdf.multi_cell(box_width - bullet_spacing, vertical_spacing, txt=safe_pdf_text(procedure['checklist_entry']))
            
            pdf.ln(vertical_spacing)

        if not rendered_any_content:
            raise ValueError(
                "No matching checklist procedures were found for this selection. "
                "Try a different profile, operation, drone platform, or fleet size."
            )
        
        # Output PDF
        output_path = os.path.join(output_folder, filename)
        pdf.output(output_path)
        print(f"✓ Checklist PDF generated: {filename}")
        return output_path

    def generate_procedure_pdf(self, output_folder, filename):
        """
        Generate a detailed A4 procedure manual PDF.
        
        Args:
            output_folder: Path to the output folder
            filename: Name of the output PDF file
        """
        ## STYLING
        font_size = 12
        section_font_size = 14
        vertical_spacing = 10
        single_par_spacing = 8
        right_margin = 20
        box_width = 200 - right_margin
        max_title_width = 125
        
        ## Initialize PDF
        pdf = FPDF(format='A4')
        pdf.set_right_margin(right_margin)
        pdf.set_font("Helvetica", size=font_size)
        rendered_any_content = False
        
        for checklist in self.checklists:
            title = checklist['title']
            color = checklist.get('color', [0, 0, 0])
            items = self.filter_sections(checklist.get('items', []))
            if not items:
                continue

            rendered_any_content = True
            page_number = 1
            pdf.add_page()
            
            # Calculate section height
            section_height = vertical_spacing
            for section in items:
                for procedure in section['procedures']:
                    entry = safe_pdf_text(procedure['checklist_entry'])
                    description = safe_pdf_text(procedure['procedure_description'])
                    entry_height = -(-pdf.get_string_width(entry + ": " + description) // (box_width-7))
                    section_height += (entry_height - 1) * single_par_spacing + vertical_spacing
            
            # Add header
            if pdf.get_y() + section_height > pdf.h - pdf.b_margin:
                self.add_branding_banner(pdf, f"{title} ({page_number})", max_title_width, vertical_spacing)
            else:
                self.add_branding_banner(pdf, f"{title}", max_title_width, vertical_spacing)
            
            self.add_metadata(pdf, font_size-3, box_width)
            pdf.set_fill_color(*color)
            pdf.rect(200, 0, 10, 297, 'F')  # Color band on the right for A4
            pdf.set_text_color(0, 0, 0)
            pdf.set_font("Helvetica", size=font_size)
            
            # Process sections
            for section in items:
                section_height = vertical_spacing
                for procedure in section['procedures']:
                    entry = safe_pdf_text(procedure['checklist_entry'])
                    description = safe_pdf_text(procedure['procedure_description'])
                    entry_height = -(-pdf.get_string_width(entry + ": " + description) // (box_width-10))
                    section_height += (entry_height - 1) * single_par_spacing + vertical_spacing

                # Check if new page is needed
                if pdf.get_y() + section_height > pdf.h - pdf.b_margin:
                    page_number += 1
                    pdf.add_page()
                    self.add_branding_banner(pdf, f"{title} ({page_number})", max_title_width, vertical_spacing)
                    self.add_metadata(pdf, font_size-3, box_width)
                    pdf.set_fill_color(*color)
                    pdf.rect(200, 0, 10, 297, 'F')
                    pdf.set_text_color(0, 0, 0)
                    pdf.set_font("Helvetica", size=font_size)

                # Draw section box
                pdf.rect(10, pdf.get_y(), box_width, section_height, 'D')
                pdf.set_fill_color(*color)
                pdf.rect(10, pdf.get_y(), box_width, vertical_spacing, 'F')
                pdf.set_font("Helvetica", style='B', size=section_font_size)
                pdf.set_text_color(255, 255, 255)
                pdf.cell(box_width, vertical_spacing, txt=safe_pdf_text(section['section']), ln=True, align='C')
                pdf.set_text_color(0, 0, 0)
                pdf.set_font("Helvetica", size=font_size)
                
                # Add procedures with descriptions
                for procedure in section['procedures']:
                    entry = safe_pdf_text(procedure['checklist_entry'])
                    description = safe_pdf_text(procedure['procedure_description'])
                    pdf.set_font("Helvetica", size=font_size, style='B')
                    pdf.write(single_par_spacing, f"{entry}: ")
                    pdf.set_font("Helvetica", size=font_size)
                    pdf.write(single_par_spacing, description)
                    pdf.ln(vertical_spacing)
            
            pdf.ln(vertical_spacing)

        if not rendered_any_content:
            raise ValueError(
                "No matching detailed procedures were found for this selection. "
                "Try a different profile, operation, drone platform, or fleet size."
            )
        
        # Output PDF
        output_path = os.path.join(output_folder, filename)
        pdf.output(output_path)
        print(f"✓ Procedure PDF generated: {filename}")
        return output_path


def get_json_files(json_dir, assembly_dir=None, assembly_insert_before="03_first_flight.json"):
    """Get JSON files in document order, with assembly inserted before first flight."""
    json_files = []

    if os.path.exists(json_dir):
        for filename in sorted(os.listdir(json_dir)):
            if filename.endswith('.json'):
                json_files.append(os.path.join(json_dir, filename))

    if not assembly_dir or not os.path.exists(assembly_dir):
        return json_files

    assembly_files = []
    for filename in sorted(os.listdir(assembly_dir)):
        if filename.endswith('.json'):
            assembly_files.append(os.path.join(assembly_dir, filename))

    if not assembly_files:
        return json_files

    insert_index = None
    for index, file_path in enumerate(json_files):
        if os.path.basename(file_path) == assembly_insert_before:
            insert_index = index
            break

    if insert_index is None:
        return json_files + assembly_files

    return json_files[:insert_index] + assembly_files + json_files[insert_index:]


def main():
    """Main function to run the checklist generator."""
    parser = argparse.ArgumentParser(
        description='Generate drone operation checklists and procedure manuals.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --operation VLOS --drone DJI --count SINGLE
  %(prog)s -o BVLOS_NO_VO -d EBEE -c MULTIPLE
    %(prog)s --profile wild --operation VLOS --drone DJI --count SINGLE
  %(prog)s --list-options

Operation Types:
  VLOS         - VLOS
  BVLOS_NO_VO  - BVLOS 1km (No Observer)
  BVLOS_VO     - BVLOS 2km (Observer)
  NIGHT_VLOS   - Night VLOS
  NIGHT_BVLOS  - Night BVLOS

Drone Platforms:
  DJI          - DJI
  EBEE         - Ebee X
  UOB_GLIDER   - UoB Glider
  SMURF        - Papa Smurf
  CODRONE      - CoDrone
  PARROT       - Parrot Anafi

Number of Drones:
  SINGLE       - Single Drone
  MULTIPLE     - Multiple Drones
  SWARM        - Swarm of Drones

Profiles:
    wild         - bundled public procedures
    template     - starter profile to copy and customize
        """
    )
    
    parser.add_argument('-o', '--operation', 
                        choices=[code for code, _ in OPERATION_TYPE_CHOICES],
                        default='VLOS',
                        help='Operation type (default: VLOS)')
    
    parser.add_argument('-d', '--drone',
                        choices=[code for code, _ in DRONE_PLATFORM_CHOICES],
                        default='DJI',
                        help='Drone platform (default: DJI)')
    
    parser.add_argument('-c', '--count',
                        choices=[code for code, _ in NUMBER_OF_DRONES_CHOICES],
                        default='SINGLE',
                        help='Number of drones (default: SINGLE)')
    
    parser.add_argument('--list-options',
                        action='store_true',
                        help='List all available options and exit')

    parser.add_argument('--list-profiles',
                        action='store_true',
                        help='List available procedure profiles and exit')

    parser.add_argument('--create-profile',
                        help='Create a new profile by copying an existing one and exit')

    parser.add_argument('--from-profile',
                        default='template',
                        help='Source profile for --create-profile (default: template)')

    parser.add_argument('--profile',
                        default='wild',
                        help='Procedure profile to use (default: wild)')
    
    parser.add_argument('--json-dir',
                        help='Override the JSON data directory for advanced use')
    
    args = parser.parse_args()

    script_dir = os.path.dirname(os.path.abspath(__file__))

    if args.list_profiles:
        profiles = list_profiles(script_dir)
        print("\nAvailable procedure profiles:")
        for profile in profiles:
            print(f"  - {profile}")
        print()
        return

    if args.create_profile:
        try:
            created = create_profile(script_dir, args.create_profile, from_profile=args.from_profile)
        except ValueError as error:
            print(f"Error: {error}")
            sys.exit(1)

        print("\nProfile created:")
        print(f"  Name: {args.create_profile}")
        print(f"  Directory: {created['profile_dir']}")
        print(f"  Edit constants: {created['constants_file']}")
        print(f"  Edit procedures: {created['json_dir']}")
        if os.path.isdir(created['assembly_dir']):
            print(f"  Edit assembly: {created['assembly_dir']}")
        print()
        return
    
    if args.list_options:
        print("\nAvailable Options:")
        print("\nOperation Types:")
        for code, name in OPERATION_TYPE_CHOICES:
            print(f"  {code:10} - {name}")
        print("\nDrone Platforms:")
        for code, name in DRONE_PLATFORM_CHOICES:
            print(f"  {code:10} - {name}")
        print("\nNumber of Drones:")
        for code, name in NUMBER_OF_DRONES_CHOICES:
            print(f"  {code:10} - {name}")
        print()
        return
    
    try:
        resolved_paths = resolve_data_paths(
            script_dir,
            profile_name=args.profile,
            json_dir_override=args.json_dir,
        )
    except ValueError as error:
        print(f"Error: {error}")
        sys.exit(1)

    # Get JSON files from the selected profile.
    # Assembly JSON is inserted before the first-flight phase so platform
    # setup appears in the expected place within the generated documents.
    json_files = get_json_files(resolved_paths['json_dir'], resolved_paths['assembly_dir'])
    
    if not json_files:
        print(f"Error: No JSON files found in {resolved_paths['json_dir']}")
        sys.exit(1)
    
    print(f"\nGenerating checklists with:")
    print(f"  Profile: {resolved_paths['profile_name']}")
    print(f"  Operation Type: {dict(OPERATION_TYPE_CHOICES)[args.operation]}")
    print(f"  Drone Platform: {dict(DRONE_PLATFORM_CHOICES)[args.drone]}")
    print(f"  Number of Drones: {dict(NUMBER_OF_DRONES_CHOICES)[args.count]}")
    print(f"  JSON Files: {len(json_files)} files loaded")
    print()
    
    # Create generator
    try:
        generator = ChecklistGenerator(
            checklist_files=json_files,
            operation_type=args.operation,
            drone_platform=args.drone,
            number_of_drones=args.count
        )
        
        # Archive existing PDFs
        print("Archiving previous PDFs...")
        generator.archive_existing_pdfs()
        print()
        
        # Generate timestamp and create output folder
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_folder = generator.create_output_folder(timestamp)
        folder_name = os.path.basename(output_folder)
        
        print(f"Creating new folder: {folder_name}/")
        print()
        
        # Generate filenames
        checklist_filename = f"checklist.pdf"
        procedure_filename = f"procedures.pdf"
        
        # Generate PDFs
        generator.generate_checklist_pdf(output_folder, checklist_filename)
        generator.generate_procedure_pdf(output_folder, procedure_filename)
        
        print("\n✓ All documents generated successfully!")
        print(f"  Output folder: output/{folder_name}/")
        print(f"    - {checklist_filename}")
        print(f"    - {procedure_filename}")
        
    except Exception as e:
        print(f"\n✗ Error generating PDFs: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
