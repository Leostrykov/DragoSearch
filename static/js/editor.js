import { Editor } from '@tiptap/core';
import { StarterKit } from '@tiptap/starter-kit';

const editor = new Editor({
  element: document.querySelector('#editor'),
  extensions: [StarterKit],
  content: '<p>Начните вводить текст...</p>',
  onUpdate: ({ editor }) => {
    const htmlContent = editor.getHTML();
    document.querySelector('#editor-content').value = htmlContent;
  },
});

window.addEventListener('DOMContentLoaded', () => {
  const initialContent = window.content;
  if (initialContent) {
    editor.commands.setContent(initialContent);
  }
});

document.querySelector('#editor-form').addEventListener('submit', (e) => {
  document.querySelector('#editor-content').value = editor.getHTML();
  e.target.submit();
});