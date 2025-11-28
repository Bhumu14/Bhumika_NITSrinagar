import re
from typing import List, Dict

class TextParser:
    def parse_line_items(self, text: str) -> List[Dict]:
        """Extract line items from bill text with better accuracy"""
        items = []
        lines = text.split('\n')
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            # Skip empty lines and obvious non-items
            if not line or self.is_header_or_total(line):
                i += 1
                continue
            
            # Try to extract item from current line
            item = self.extract_hospital_item(line) or \
                   self.extract_pharmacy_item(line) or \
                   self.extract_structured_item(line, lines, i)
            
            if item and self.is_valid_item(item):
                items.append(item)
                # Skip next line if we consumed multi-line item
                if item.get('multi_line', False):
                    i += 1
            
            i += 1
        
        return items
    
    def is_header_or_total(self, line: str) -> bool:
        """Check if line is a header, total, or other non-item text"""
        lower_line = line.lower()
        skip_patterns = [
            'total', 'subtotal', 'grand total', 'net amount', 'final bill',
            'bill no', 'patient name', 'page', 'date', 's.no', 'particulars',
            'rate', 'qty', 'amount', 'hospita', 'consult', 'address',
            'description', 'hsn', 'batch', 'exp', 'gst', 'tax', 'discount'
        ]
        
        return any(pattern in lower_line for pattern in skip_patterns) or \
               re.match(r'^[\.\-\=\*\s]*$', line) or \
               len(line) < 3
    
    def extract_hospital_item(self, line: str) -> Dict:
        """Extract items from hospital bill format like train_sample_1"""
        # Pattern: "1. 15/11/2025 R1001 2D echocardiography 1180.00 x 1.00 1180.00"
        patterns = [
            r'(\d+)\.\s+(\d{2}/\d{2}/\d{4})\s+(\w+)\s+(.+?)\s+(\d+\.?\d*)\s*x\s*(\d+\.?\d*)\s+(\d+\.?\d*)',
            r'(\d+)\.\s+(.+?)\s+(\d+\.?\d*)\s*x\s*(\d+\.?\d*)\s+(\d+\.?\d*)',
            r'(\d+)\.\s+(.+?)\s+(\d+\.?\d*)\s+(\d+\.?\d*)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, line)
            if match:
                try:
                    groups = match.groups()
                    if len(groups) == 7:  # Full hospital format
                        item_name = groups[3].strip()
                        rate = float(groups[4])
                        quantity = float(groups[5])
                        amount = float(groups[6])
                    elif len(groups) == 5:  # Medium format
                        item_name = groups[1].strip()
                        rate = float(groups[2])
                        quantity = float(groups[3])
                        amount = float(groups[4])
                    elif len(groups) == 4:  # Simple format
                        item_name = groups[1].strip()
                        rate = float(groups[2])
                        quantity = 1.0
                        amount = float(groups[3])
                    else:
                        continue
                    
                    # Clean item name
                    item_name = self.clean_item_name(item_name)
                    
                    return {
                        "item_name": item_name,
                        "item_amount": amount,
                        "item_rate": rate,
                        "item_quantity": quantity
                    }
                    
                except (ValueError, IndexError):
                    continue
        
        return None
    
    def extract_pharmacy_item(self, line: str) -> Dict:
        """Extract items from pharmacy bills like train_sample_2"""
        # Pattern for table rows with medicine names and amounts
        patterns = [
            # Pharmacy table format: "1 3004 13825755 09/28 CANNULA 22 NO 1 105.00 0.00 105.00 5"
            r'(\d+)\s+(\w+)\s+(\w+)\s+(\S+)\s+(.+?)\s+(\d+\.?\d*)\s+(\d+\.?\d*)\s+(\d+\.?\d*)\s+(\d+\.?\d*)\s+(\d+)',
            # Simpler pharmacy format
            r'(\d+)\s+(.+?)\s+(\d+\.?\d*)\s+(\d+\.?\d*)\s+(\d+\.?\d*)$',
            # Medicine name followed by amount
            r'([A-Z][A-Za-z\s]+(?:\s+[A-Z][A-Za-z]*)*)\s+(\d+\.?\d*)$'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, line)
            if match:
                try:
                    groups = match.groups()
                    if len(groups) == 10:  # Full pharmacy table
                        item_name = groups[4].strip()
                        amount = float(groups[8])  # Amount column
                    elif len(groups) == 5:  # Medium format
                        item_name = groups[1].strip()
                        amount = float(groups[4])
                    elif len(groups) == 2:  # Simple name + amount
                        item_name = groups[0].strip()
                        amount = float(groups[1])
                    else:
                        continue
                    
                    # Clean and validate
                    item_name = self.clean_item_name(item_name)
                    if not self.looks_like_medicine(item_name):
                        continue
                    
                    return {
                        "item_name": item_name,
                        "item_amount": amount,
                        "item_rate": None,
                        "item_quantity": None
                    }
                    
                except (ValueError, IndexError):
                    continue
        
        return None
    
    def extract_structured_item(self, line: str, all_lines: List[str], current_index: int) -> Dict:
        """Extract structured items that might span multiple lines"""
        # Look for medicine-like patterns
        medicine_patterns = [
            r'([A-Z][A-Za-z\s]+(?:[\d\.]*(?:\s*[MG]G)?\s*(?:TAB|CAP|INJ|SYR|SYP|CREAM|OINTMENT|GEL|LOTION|SPRAY|POWDER|SOLUTION|DROPS)?))',
            r'([A-Z][A-Za-z]+\s+[A-Z][A-Za-z]+\s+(?:TAB|CAP|INJ|SYR))'
        ]
        
        for pattern in medicine_patterns:
            match = re.search(pattern, line)
            if match:
                item_name = match.group(1).strip()
                
                # Look for amount in current or next line
                amount = self.find_amount_nearby(line, all_lines, current_index)
                
                if amount and self.looks_like_medicine(item_name):
                    return {
                        "item_name": item_name,
                        "item_amount": amount,
                        "item_rate": None,
                        "item_quantity": None,
                        "multi_line": True
                    }
        
        return None
    
    def find_amount_nearby(self, current_line: str, all_lines: List[str], current_index: int) -> float:
        """Find amount near the current line"""
        # Check current line
        amount_match = re.search(r'(\d+\.?\d*)$', current_line)
        if amount_match:
            try:
                return float(amount_match.group(1))
            except ValueError:
                pass
        
        # Check next line
        if current_index + 1 < len(all_lines):
            next_line = all_lines[current_index + 1].strip()
            amount_match = re.search(r'(\d+\.?\d*)$', next_line)
            if amount_match:
                try:
                    amount = float(amount_match.group(1))
                    # Validate it's a reasonable amount
                    if 0.1 <= amount <= 100000:
                        return amount
                except ValueError:
                    pass
        
        return None
    
    def clean_item_name(self, name: str) -> str:
        """Clean and normalize item names"""
        # Remove common prefixes/suffixes and clean up
        name = re.sub(r'^\d+\.?\s*', '', name)  # Remove leading numbers
        name = re.sub(r'\s+[Xx]\s+\d+\.?\d*', '', name)  # Remove "x quantity"
        name = re.sub(r'\s*\d+\.?\d*\s*$', '', name)  # Remove trailing numbers
        name = re.sub(r'\s+', ' ', name)  # Normalize spaces
        return name.strip()
    
    def looks_like_medicine(self, name: str) -> bool:
        """Check if the text looks like a medicine name"""
        if len(name) < 3:
            return False
        
        # Common medicine patterns
        medicine_indicators = [
            'tab', 'cap', 'inj', 'syr', 'syp', 'cream', 'ointment', 'gel',
            'mg', 'gm', 'ml', 'iv', 'oral', 'topical', 'injection'
        ]
        
        # Check for medicine-like words
        lower_name = name.lower()
        if any(indicator in lower_name for indicator in medicine_indicators):
            return True
        
        # Check for proper capitalization (medicine names often have mixed case)
        if re.match(r'^[A-Z][a-z]+(?:\s+[A-Z][a-z]*)*', name):
            return True
        
        return len(name) >= 4 and not name.isdigit()
    
    def is_valid_item(self, item: Dict) -> bool:
        """Validate if extracted item makes sense"""
        # Check amount range
        amount = item.get('item_amount', 0)
        if not (0.1 <= amount <= 100000):
            return False
        
        # Check item name
        name = item.get('item_name', '')
        if len(name) < 2 or name.isdigit():
            return False
        
        # Skip obvious non-items
        skip_words = ['total', 'subtotal', 'date', 'page', 'bill', 'no.']
        if any(skip_word in name.lower() for skip_word in skip_words):
            return False
        
        return True
    
    def detect_page_type(self, text: str) -> str:
        """Detect if page is Bill Detail, Final Bill, or Pharmacy"""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ['pharmacy', 'medicos', 'drug', 'cash memo', 'medicine']):
            return "Pharmacy"
        elif any(word in text_lower for word in ['final bill', 'grand total', 'net amount payable']):
            return "Final Bill"
        else:
            return "Bill Detail"