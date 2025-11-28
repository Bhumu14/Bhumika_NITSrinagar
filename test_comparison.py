import os
from utils.image_processor import ImageProcessor
from utils.text_parser import TextParser

def compare_parsing():
    """Compare old simple parsing vs new improved parsing"""
    
    training_path = r"C:\Users\DELL\Downloads\TRAINING_SAMPLES\TRAINING_SAMPLES"
    test_file = 'train_sample_1.pdf'
    file_path = os.path.join(training_path, test_file)
    
    processor = ImageProcessor()
    
    # Get the text first
    pages = processor.process_document(file_path)
    all_text = "\n".join(page['text'] for page in pages)
    
    print("=" * 70)
    print("🔄 OLD vs NEW PARSING COMPARISON")
    print("=" * 70)
    
    # Old simple parsing (from your original text_parser.py)
    def old_simple_parse(text):
        items = []
        lines = text.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Simple pattern matching for line items
            try:
                # Pattern for: "Item Name  Quantity  Rate  Amount"
                pattern1 = r'(.+?)\s+(\d+\.?\d*)\s+(\d+\.?\d*)\s+(\d+\.?\d*)'
                match1 = re.search(pattern1, line)
                
                if match1 and len(match1.groups()) == 4:
                    item_name = match1.group(1).strip()
                    quantity = float(match1.group(2))
                    rate = float(match1.group(3))
                    amount = float(match1.group(4))
                    
                    expected_amount = rate * quantity
                    if abs(amount - expected_amount) < (expected_amount * 0.2):
                        return {
                            "item_name": item_name,
                            "item_amount": amount,
                            "item_rate": rate,
                            "item_quantity": quantity
                        }
                
                # Pattern for items with just name and amount
                pattern2 = r'(.+?)\s+(\d+\.?\d*)$'
                match2 = re.search(pattern2, line)
                if match2 and len(match2.groups()) == 2:
                    item_name = match2.group(1).strip()
                    amount = float(match2.group(2))
                    
                    if 1 <= amount <= 10000:
                        return {
                            "item_name": item_name,
                            "item_amount": amount,
                            "item_rate": None,
                            "item_quantity": None
                        }
                        
            except (ValueError, AttributeError):
                pass
                
        return None
    
    # Import re for old parsing
    import re
    
    # Old parsing
    print("\n📋 OLD PARSING RESULTS:")
    print("-" * 40)
    old_items = []
    lines = all_text.split('\n')
    for line in lines:
        item = old_simple_parse(line)
        if item:
            old_items.append(item)
    
    print(f"Items found: {len(old_items)}")
    old_total = sum(item['item_amount'] for item in old_items)
    print(f"Total amount: ₹{old_total:.2f}")
    print("Sample items (first 10):")
    for i, item in enumerate(old_items[:10], 1):
        print(f"  {i}. {item['item_name'][:30]}... - ₹{item['item_amount']:.2f}")
    
    # New parsing
    print("\n📋 NEW IMPROVED PARSING RESULTS:")
    print("-" * 40)
    parser = TextParser()
    new_items = parser.parse_line_items(all_text)
    
    print(f"Items found: {len(new_items)}")
    new_total = sum(item['item_amount'] for item in new_items)
    print(f"Total amount: ₹{new_total:.2f}")
    print("All items found:")
    for i, item in enumerate(new_items, 1):
        rate = item.get('item_rate', 'N/A')
        qty = item.get('item_quantity', 'N/A')
        print(f"  {i:2d}. {item['item_name'][:40]:40} ₹{item['item_amount']:8.2f} (Rate: {rate}, Qty: {qty})")
    
    print("\n📊 COMPARISON SUMMARY:")
    print(f"   Old parser found: {len(old_items)} items, Total: ₹{old_total:.2f}")
    print(f"   New parser found: {len(new_items)} items, Total: ₹{new_total:.2f}")
    print(f"   Actual Bill Total (from PDF): ₹73,420.25")
    
    accuracy_old = min(old_total, 73420.25) / max(old_total, 73420.25) * 100
    accuracy_new = min(new_total, 73420.25) / max(new_total, 73420.25) * 100
    
    print(f"   Accuracy - Old: {accuracy_old:.1f}%")
    print(f"   Accuracy - New: {accuracy_new:.1f}%")

if __name__ == "__main__":
    compare_parsing()