// Простий тест для утиліт
export const formatDate = (date: Date): string => {
  return date.toLocaleDateString('uk-UA');
};

export const formatCurrency = (amount: number, currency: string = 'USD'): string => {
  return new Intl.NumberFormat('uk-UA', {
    style: 'currency',
    currency: currency
  }).format(amount);
};

export const validateEmail = (email: string): boolean => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
};

export const truncateText = (text: string, maxLength: number): string => {
  if (text.length <= maxLength) return text;
  return text.substring(0, maxLength) + ' ...';
};

describe('Utility Functions', () => {
  test('formatDate formats date correctly', () => {
    const testDate = new Date('2025-01-30');
    const formatted = formatDate(testDate);
    expect(formatted).toBeDefined();
    expect(typeof formatted).toBe('string');
  });

  test('formatCurrency formats amount correctly', () => {
    const amount = 1000;
    const formatted = formatCurrency(amount);
    expect(formatted).toBeDefined();
    expect(typeof formatted).toBe('string');
    expect(formatted).toContain('1\u00A0000,00');
  });

  test('formatCurrency handles different currencies', () => {
    const amount = 500;
    const formatted = formatCurrency(amount, 'EUR');
    expect(formatted).toBeDefined();
    expect(formatted).toContain('500');
    expect(formatted).toContain('EUR');
  });

  test('validateEmail validates correct emails', () => {
    expect(validateEmail('test@example.com')).toBe(true);
    expect(validateEmail('user.name@domain.co.uk')).toBe(true);
    expect(validateEmail('invalid-email')).toBe(false);
    expect(validateEmail('test@')).toBe(false);
    expect(validateEmail('@domain.com')).toBe(false);
  });

  test('truncateText truncates long text', () => {
    const longText = 'This is a very long text that needs to be truncated';
    const truncated = truncateText(longText, 20);
    expect(truncated).toContain('This is a very long');
    expect(truncated).toContain('...');
    expect(truncated.length).toBeGreaterThan(20);
  });

  test('truncateText keeps short text unchanged', () => {
    const shortText = 'Short text';
    const result = truncateText(shortText, 20);
    expect(result).toBe(shortText);
  });

  test('truncateText handles empty string', () => {
    const result = truncateText('', 10);
    expect(result).toBe('');
  });
}); 