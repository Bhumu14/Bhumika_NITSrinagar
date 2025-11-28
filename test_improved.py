import os
from utils.image_processor import ImageProcessor
from utils.text_parser import TextParser

def test_improved_parsing():
    """Test the improved parsing with your training samples"""
    
    training_path = r"C:\Users\DELL\Downloads\TRAINING_SAMPLES\TRAINING_SAMPLES"
    test_files = ['train_sample_1.pdf', 'train_sample_2.pdf', 'train_sample_3.pdf']
    
    processor = ImageProcessor()
    parser = TextParser()
    
    for file_name in test_files:
        file_path = os.path.join(training_path, file_name)
        
        if not os.path.exists(file_path):
            print(f"❌ File not found: {file_path}")
            continue
        
        print(f"\n{'='*60}")
        print(f"🔬 TESTING: {file_name}")
        print(f"{'='*60}")
        
        try:
            # Process the file
            pages = processor.process_document(file_path)
            
            total_items = 0
            total_amount = 0
            
            for page in pages:
                page_type = parser.detect_page_type(page['text'])
                print(f"\n📄 Page {page['page_no']} - Type: {page_type}")
                print("-" * 50)
                
                # Parse items
                items = parser.parse_line_items(page['text'])
                
                print(f"✅ Found {len(items)} valid items:")
                for i, item in enumerate(items, 1):
                    # Get values safely
                    rate_value = item.get('item_rate')
                    quantity_value = item.get('item_quantity')
                    
                    # Format rate display
                    if rate_value is not None:
                        rate_display = f"{rate_value:6.2f}"
                    else:
                        rate_display = "   N/A"
                    
                    # Format quantity display  
                    if quantity_value is not None:
                        quantity_display = f"{quantity_value:4.1f}"
                    else:
                        quantity_display = " N/A"
                    
                    print(f"   {i:2d}. {item['item_name'][:40]:40} "
                          f"₹{item['item_amount']:8.2f} "
                          f"(Rate: {rate_display} "
                          f"Qty: {quantity_display})")
                    
                    total_amount += item['item_amount']
                
                total_items += len(items)
            
            print(f"\n📊 FINAL SUMMARY for {file_name}:")
            print(f"   Total Items: {total_items}")
            print(f"   Total Amount: ₹{total_amount:.2f}")
            
            # Show some raw text for comparison
            if pages:
                print(f"\n🔍 Raw text sample (first 500 chars):")
                print(pages[0]['text'][:500])
            
        except Exception as e:
            print(f"❌ Error processing {file_name}: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    test_improved_parsing()