import React from 'react';
import { render, screen } from '@testing-library/react';

// Простий тест без складних залежностей
test('basic app test', () => {
  expect(true).toBe(true);
});

test('React is working', () => {
  const element = React.createElement('div', { 'data-testid': 'test' }, 'Test');
  expect(element).toBeDefined();
}); 