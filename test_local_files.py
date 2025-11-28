import requests
import json
import os

def test_with_local_files():
    """Test with the training sample files from your Downloads folder"""
    
    # Correct path to your training samples
    training_samples_path = r"C:\Users\DELL\Downloads\TRAINING_SAMPLES\TRAINING_SAMPLES"
    
    # List of files in that directory
    try:
        files_in_dir = os.listdir(training_samples_path)
        print(f"Files found in directory: {files_in_dir}")
    except FileNotFoundError:
        print(f"❌ Directory not found: {training_samples_path}")
        return
    
    # List of specific files to test (use the ones you have)
    local_files = []
    for file in files_in_dir:
        if file.endswith(('.pdf', '.png', '.jpg', '.jpeg')):
            full_path = os.path.join(training_samples_path, file)
            local_files.append(full_path)
    
    if not local_files:
        print("❌ No PDF or image files found in the directory")
        return
    
    print(f"Found {len(local_files)} files to process")
    
    for file_path in local_files[:3]:  # Test first 3 files
        print(f"\n{'='*50}")
        print(f"=== Testing with {os.path.basename(file_path)} ===")
        print(f"Full path: {file_path}")
        
        # Import and process
        from utils.image_processor import ImageProcessor
        from utils.text_parser import TextParser
        
        processor = ImageProcessor()
        parser = TextParser()
        
        try:
            # Process the local file
            pages = processor.process_document(file_path)
            
            all_items = []
            for page in pages:
                print(f"\n📄 Page {page['page_no']}")
                print(f"Text length: {len(page['text'])} characters")
                print("-" * 40)
                
                # Show first 300 characters of text
                preview_text = page['text'][:300].replace('\n', ' ')
                print(f"Text preview: {preview_text}...")
                
                # Parse the text
                items = parser.parse_line_items(page['text'])
                all_items.extend(items)
                
                print(f"✅ Found {len(items)} items on this page")
                for i, item in enumerate(items, 1):
                    print(f"  {i}. {item['item_name']}: ₹{item['item_amount']} "
                          f"(Rate: {item.get('item_rate', 'N/A')}, "
                          f"Qty: {item.get('item_quantity', 'N/A')})")
            
            print(f"\n📊 SUMMARY for {os.path.basename(file_path)}:")
            print(f"✅ Total items found: {len(all_items)}")
            total_amount = sum(item['item_amount'] for item in all_items)
            print(f"✅ Total amount: ₹{total_amount:.2f}")
            
        except Exception as e:
            print(f"❌ Error processing {file_path}: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    test_with_local_files()