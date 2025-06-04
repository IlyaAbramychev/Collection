import React from 'react';
import styled from 'styled-components';
import { Link } from 'react-router-dom';
import Button from './Button';

const Container = styled.div`
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background-color: ${({ theme }) => theme.background};
  color: ${({ theme }) => theme.text};
`;

const Title = styled.h1`
  margin-bottom: 20px;
  font-size: 2rem;
`;

const Info = styled.p`
  margin-bottom: 40px;
  text-align: center;
  max-width: 600px;
`;

const Buttons = styled.div`
  display: flex;
  gap: 20px;
`;

const WelcomeScreen: React.FC = () => (
  <Container>
    <Title>Добро пожаловать в \"Сборник\"</Title>
    <Info>
      Это платформа для публикации и обмена знаниями. Если у вас уже есть аккаунт, войдите. Новым пользователям доступна регистрация.
    </Info>
    <Buttons>
      <Link to="/login">
        <Button>Войти</Button>
      </Link>
      <Link to="/register">
        <Button>Регистрация</Button>
      </Link>
    </Buttons>
  </Container>
);

export default WelcomeScreen;
