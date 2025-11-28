from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from utils.image_processor import ImageProcessor
from utils.text_parser import TextParser
import traceback

app = FastAPI(
    title="Bajaj Health Bill Processor",
    version="1.0.0",
    description="API for extracting line items from medical bills"
)

# Initialize processors
try:
    image_processor = ImageProcessor()
    text_parser = TextParser()
    processors_available = True
except Exception as e:
    print(f"Processor initialization failed: {e}")
    processors_available = False

class BillItem(BaseModel):
    item_name: str
    item_amount: float
    item_rate: Optional[float] = None
    item_quantity: Optional[float] = None

class PageData(BaseModel):
    page_no: str
    page_type: str
    bill_items: List[BillItem]

class ResponseData(BaseModel):
    pagewise_line_items: List[PageData]
    total_item_count: int
    reconciled_amount: float

class TokenUsage(BaseModel):
    total_tokens: int = 0
    input_tokens: int = 0
    output_tokens: int = 0

class BillResponse(BaseModel):
    is_success: bool
    token_usage: TokenUsage
    data: Optional[ResponseData] = None

class BillRequest(BaseModel):
    document: str

@app.get("/")
async def root():
    return {"message": "Bajaj Health Bill Processor API", "status": "healthy"}

@app.post("/extract-bill-data", response_model=BillResponse)
async def extract_bill_data(request: BillRequest):
    """
    Extract bill data from document URL
    """
    try:
        if not processors_available:
            raise HTTPException(status_code=500, detail="Processors not available")
        
        print(f"Processing document: {request.document}")
        
        # Process the document
        pages_data = image_processor.process_document(request.document)
        
        pagewise_line_items = []
        all_items = []
        
        for page in pages_data:
            page_text = page["text"]
            page_no = page["page_no"]
            
            # Parse the text to extract line items
            items = text_parser.parse_line_items(page_text)
            
            # Detect page type
            page_type = text_parser.detect_page_type(page_text)
            
            # Convert to BillItem objects
            bill_items = []
            for item in items:
                bill_item = BillItem(
                    item_name=item["item_name"],
                    item_amount=item["item_amount"],
                    item_rate=item.get("item_rate"),
                    item_quantity=item.get("item_quantity")
                )
                bill_items.append(bill_item)
                all_items.append(bill_item)
            
            # Create page data
            page_data = PageData(
                page_no=page_no,
                page_type=page_type,
                bill_items=bill_items
            )
            pagewise_line_items.append(page_data)
        
        # Calculate totals
        total_amount = sum(item.item_amount for item in all_items)
        
        response_data = ResponseData(
            pagewise_line_items=pagewise_line_items,
            total_item_count=len(all_items),
            reconciled_amount=total_amount
        )
        
        return BillResponse(
            is_success=True,
            token_usage=TokenUsage(),
            data=response_data
        )
        
    except Exception as e:
        print(f"Error processing document: {str(e)}")
        traceback.print_exc()
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to process document: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)