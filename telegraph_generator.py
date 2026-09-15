import logging
import markdown
from telegraph import Telegraph

# Use a persistent Telegraph account to avoid rate limits on Render
telegraph = Telegraph(access_token='2331b63c27557de84d9a0369818028ed0b4dae84f8cb3576b813387b382c')

def create_protocol_page(title, markdown_text):
    """
    Converts markdown text to HTML, then publishes it as a Telegraph page.
    Returns the URL of the published page.
    """
    try:
        # Telegraph only supports h3 and h4, NOT h1 and h2
        # So we convert all # and ## to ###
        markdown_text = markdown_text.replace('\n# ', '\n### ')
        markdown_text = markdown_text.replace('\n## ', '\n### ')
        if markdown_text.startswith('# '):
            markdown_text = '### ' + markdown_text[2:]
        if markdown_text.startswith('## '):
            markdown_text = '### ' + markdown_text[3:]
            
        # 1. Convert Markdown to HTML
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
        err_msg = str(e)
        logging.error(f"Telegraph error: {err_msg}")
        return f"ERROR: {err_msg}"
