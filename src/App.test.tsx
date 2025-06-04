import React from 'react';
import { render, screen } from '@testing-library/react';
import App from './App';

test('renders welcome screen', () => {
  render(<App />);
  const titleElement = screen.getByText(/Добро пожаловать/i);
  expect(titleElement).toBeInTheDocument();
});
