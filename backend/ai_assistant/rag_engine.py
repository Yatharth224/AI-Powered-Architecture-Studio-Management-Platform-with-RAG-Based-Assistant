import os
import re
from django.conf import settings

KNOWLEDGE_BASE_DIR = os.path.join(
    settings.BASE_DIR, 'ai_assistant', 'knowledge_base'
)

def load_all_documents():
    """
    knowledge_base folder ki saari .txt files
    padhta hai aur unka content return karta hai
    """
    documents = {}
    for filename in os.listdir(KNOWLEDGE_BASE_DIR):
        if filename.endswith('.txt'):
            filepath = os.path.join(KNOWLEDGE_BASE_DIR, filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                documents[filename] = f.read()
    return documents



def chunk_projects_file(text):
    """
    projects.txt ko har PROJECT ke hisaab se
    todta hai (word count se nahi, structure se)
    """
    chunks = []

    # "Project:" se shuru hone wale har block
    # ko alag chunk banao
    project_blocks = re.split(r'\n(?=Project:)', text)

    for block in project_blocks:
        if not block.strip().startswith('Project:'):
            continue  # header/intro text skip karo

        # Metadata nikalo regex se
        title_match    = re.search(r'Project:\s*(.+)', block)
        category_match = re.search(r'Category:\s*(.+)', block)
        area_match      = re.search(r'Area:\s*(.+)', block)
        budget_match    = re.search(r'Budget:\s*(.+)', block)
        image_match     = re.search(r'Image:\s*(.+)', block)

        chunk = {
            'text':     block.strip(),
            'title':    title_match.group(1).strip() if title_match else '',
            'category': category_match.group(1).strip() if category_match else '',
            'area':      area_match.group(1).strip() if area_match else '',
            'budget':    budget_match.group(1).strip() if budget_match else '',
            'image':     image_match.group(1).strip() if image_match else None,
            'source':    'projects.txt'
        }
        chunks.append(chunk)

    return chunks



def chunk_simple_text(text, source_name, chunk_size=150):
    """
    Simple documents (company_profile, services, faq)
    ke liye — paragraph-wise chunk karta hai
    """
    # Pehle paragraphs mein todo (blank line se)
    paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]

    chunks = []
    for para in paragraphs:
        if len(para.split()) < 10:
            continue  # bahut chhote paragraphs (headings) skip karo

        chunks.append({
            'text':     para,
            'title':    None,
            'category': None,
            'area':     None,
            'budget':   None,
            'image':    None,
            'source':   source_name
        })

    return chunks



