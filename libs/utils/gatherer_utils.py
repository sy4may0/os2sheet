def remove_comment(text: str, comment: str = '#'):
    result = []
    for l in text.splitlines():
        stripped_l = l.strip()
        if not stripped_l or stripped_l.startswith(comment):
            continue
        
        comment_index = l.find(comment)
        if not comment_index == -1:
            l = l[:comment_index].rstrip()
        
        result.append(l)
    
    return result
