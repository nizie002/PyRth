// Right sidebar table of contents handler
document.addEventListener('DOMContentLoaded', function() {
  // Get the table of contents
  var toc = document.querySelector('.toctree-wrapper, .contents.local.topic');
  
  if (toc) {
    // Create a container for the right sidebar TOC
    var tocWrap = document.createElement('div');
    tocWrap.className = 'toc-wrap';
    
    // Clone the TOC
    var tocClone = toc.cloneNode(true);
    
    // Add a header to the TOC
    var tocHeader = document.createElement('p');
    tocHeader.className = 'caption';
    tocHeader.textContent = 'On This Page';
    tocWrap.appendChild(tocHeader);
    
    // Add the cloned TOC to the wrapper
    tocWrap.appendChild(tocClone);
    
    // Add the TOC wrapper to the document at the beginning of the content area
    var docElement = document.querySelector('.document');
    if (docElement) {
      // Insert at the beginning of the content, rather than appending to the end
      docElement.insertBefore(tocWrap, docElement.firstChild);
      
      // Hide the original TOC to prevent duplication
      toc.style.display = 'none';
    }
  }
});