import logging
import markdown
from telegraph import Telegraph

# Initialize Telegraph account (we can reuse this)
telegraph = Telegraph()
try:
    telegraph.create_account(short_name='BayaBooks', author_name='Baya Books')
except Exception as e:
    logging.error(f"Failed to create Telegraph account: {e}")

def create_protocol_page(title, markdown_text):
    """
    Converts markdown text to HTML, then publishes it as a Telegraph page.
    Returns the URL of the published page.
    """
    try:
        # 1. Convert Markdown to HTML
        # Telegraph supports basic HTML tags (b, i, u, s, a, p, br, h3, h4, ul, ol, li, etc)
        html_content = markdown.markdown(markdown_text)
        
        # 2. Publish to Telegraph
        response = telegraph.create_page(
            title=title,
            html_content=html_content,
            author_name='Baya Books 📚',
            author_url='https://t.me/baya_books'
        )
        return response['url']
    except Exception as e:
        logging.error(f"Telegraph error: {e}")
        return None
