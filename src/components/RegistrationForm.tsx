import React, { useState } from 'react';
import styled from 'styled-components';

const PageContainer = styled.div`
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background-color: ${({ theme }) => theme.background};
`;

const FormContainer = styled.div`
  width: 100%;
  max-width: 400px;
  padding: 20px;
  background-color: #ffffff;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
`;

const FormTitle = styled.h2`
  font-size: 1.5rem;
  margin-bottom: 20px;
  text-align: center;
`;

const FormField = styled.div`
  margin-bottom: 15px;
`;

const Label = styled.label`
  display: block;
  margin-bottom: 5px;
  font-weight: bold;
`;

const Input = styled.input`
  width: 100%;
  padding: 10px;
  border: 1px solid #cccccc;
  border-radius: 4px;
  font-size: 1rem;
`;

const SubmitButton = styled.button`
  width: 100%;
  padding: 10px;
  background-color: #007bff;
  color: #ffffff;
  border: none;
  border-radius: 4px;
  font-size: 1rem;
  cursor: pointer;
  margin-top: 10px;

  &:hover {
    background-color: #0056b3;
  }
`;

const RegistrationForm: React.FC = () => {
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
  });

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: value,
    });
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    console.log('Form data submitted:', formData);
  };

  return (
    <PageContainer>
      <FormContainer>
        <FormTitle>Регистрация</FormTitle>
        <form onSubmit={handleSubmit}>
          <FormField>
            <Label htmlFor="username">Имя пользователя</Label>
            <Input
              type="text"
              id="username"
              name="username"
              value={formData.username}
              onChange={handleChange}
              required
            />
          </FormField>
          <FormField>
            <Label htmlFor="email">Электронная почта</Label>
            <Input
              type="email"
              id="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              required
            />
          </FormField>
          <FormField>
            <Label htmlFor="password">Пароль</Label>
            <Input
              type="password"
              id="password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              required
            />
          </FormField>
          <SubmitButton type="submit">Зарегистрироваться</SubmitButton>
        </form>
      </FormContainer>
    </PageContainer>
  );
};

export default RegistrationForm;
