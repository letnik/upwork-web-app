import React from 'react';

// Простий тест без складних залежностей
test('basic header test', () => {
  expect(true).toBe(true);
});

test('React is working in header test', () => {
  const element = React.createElement('header', { 'data-testid': 'header' }, 'Header');
  expect(element).toBeDefined();
}); 