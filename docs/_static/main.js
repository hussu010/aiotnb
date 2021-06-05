/* Parts of this code are Copyright (c) Rapptz.
  Used with permission.
*/

'use-strict';
let toTop;

function scrollToTop() {
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

document.addEventListener('DOMContentLoaded', () => {
  toTop = document.getElementById('to-top');
  toTop.hidden = !(window.scrollY > 0);


  const tables = document.querySelectorAll('.py-attribute-table[data-move-to-id]');
  tables.forEach(table => {
    let element = document.getElementById(table.getAttribute('data-move-to-id'));
    let parent = element.parentNode;
    // insert ourselves after the element
    parent.insertBefore(table, element.nextSibling);
  });

  window.addEventListener('scroll', () => {
    toTop.hidden = !(window.scrollY > 0);
  });
});
