import React from 'react';
import { render, screen } from '@testing-library/react';
import App from './App';

test('renders main app layout', () => {
  render(<App />);
  const element = screen.getByText(/POS/i); // Replace with something real from your App
  expect(element).toBeInTheDocument();
});
