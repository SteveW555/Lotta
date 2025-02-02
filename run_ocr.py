from pathlib import Path
from main import extract_table_majority_vote

def main():
    # Path to the image file
    #image_path = Path('data/images/ocr.jpg')
    #image_path = Path('data/images/ocrGood.png')
    image_path = Path('data/images/book.png')
    
    # Read the image bytes  
    with open(image_path, 'rb') as f:
        image_bytes = f.read()
    
    # Process the image
    try:
        results = extract_table_majority_vote(image_bytes)
        
        # Print results in a readable format
        print("\nExtracted Table Data:")
        print("-" * 50)
        for i, record in enumerate(results, 1):
            print(f"\nRecord {i}:")
            for field, value in record.items():
                print(f"{field}: {value}")
            print("-" * 30)
            
    except Exception as e:
        print(f"Error processing image: {str(e)}")

if __name__ == "__main__":
    main()