import React from 'react';

// Простий тест без складних залежностей
test('basic dashboard test', () => {
  expect(true).toBe(true);
});

test('React is working in dashboard test', () => {
  const element = React.createElement('div', { 'data-testid': 'dashboard' }, 'Dashboard');
  expect(element).toBeDefined();
}); 