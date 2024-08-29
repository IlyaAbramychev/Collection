import React from 'react';
import styled from 'styled-components';
import { Link } from 'react-router-dom'; // Импортируем Link для маршрутизации
import Button from './Button';
import logo from '../assets/logo.png';

const HeaderContainer = styled.header`
  background-color: ${({ theme }) => theme.background};
  padding: 15px 30px;
  display: flex;
  align-items: center;
  justify-content: space-between;
`;

const NavLinks = styled.nav`
  display: flex;
  align-items: center;

  a {
    color: ${({ theme }) => theme.text};
    text-decoration: none;
    margin-right: 30px; /* Увеличено расстояние между ссылками */
    font-size: 18px; /* Увеличен размер шрифта */

    &:hover {
      color: ${({ theme }) => theme.link};
    }

    &:last-child {
      margin-right: 50px; /* Увеличен правый отступ последней ссылки (Научпоп) */
    }
  }
`;

const SearchContainer = styled.div`
  display: flex;
  align-items: center;

  input {
    border: 1px solid ${({ theme }) => theme.text};
    background-color: ${({ theme }) => theme.background};
    color: ${({ theme }) => theme.text};
    padding: 8px 12px; /* Увеличен размер padding для большего комфорта */
    border-radius: 4px;
    margin-right: 20px; /* Добавлено пространство между полем ввода и кнопками */
    font-size: 16px; /* Увеличен размер шрифта в поле ввода */
  }

  button {
    margin-left: 10px; /* Увеличено расстояние между кнопками */
  }
`;

const Logo = styled.div`
  flex: 1;
  display: flex;
  align-items: center;

  img {
    height: 40px;
    margin-right: 10px;
  }
`;

interface HeaderProps {
  toggleTheme: () => void;
}

const Header: React.FC<HeaderProps> = ({ toggleTheme }) => {
  return (
    <HeaderContainer>
      <Logo>
        <Link to="/">
          <img src={logo} alt="Logo" /> {/* Используйте импортированный путь к логотипу */}
        </Link>
      </Logo>
      <NavLinks>
        <a href="#">Моя лента</a>
        <a href="#">Все потоки</a>
        <a href="#">Разработка</a>
        <a href="#">Администрирование</a>
        <a href="#">Дизайн</a>
        <a href="#">Менеджмент</a>
        <a href="#">Маркетинг</a>
        <a href="#">Научпоп</a>
      </NavLinks>
      <SearchContainer>
        <input type="text" placeholder="Поиск" />
        <Button onClick={toggleTheme}>Переключить тему</Button>
        <Link to="/register">
          <Button>Регистрация</Button> {/* Обернута в Link для маршрутизации */}
        </Link>
        <Link to="/login">
          <Button>Войти</Button> {/* Обернута в Link для маршрутизации */}
        </Link>
      </SearchContainer>
    </HeaderContainer>
  );
};

export default Header;
