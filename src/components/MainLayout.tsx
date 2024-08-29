import React from 'react';
import styled from 'styled-components';
import { FaBlog } from 'react-icons/fa'; // Импортируем иконки из библиотеки react-icons

const LayoutContainer = styled.div`
  display: flex;
  justify-content: space-between;
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
  background-color: #f9f9f9;
  border-radius: 8px;
`;

const MainContent = styled.main`
  flex: 3;
  margin-right: 20px;
  padding: 20px;
  background-color: #ffffff;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
`;

const Sidebar = styled.aside`
  flex: 1;
  background-color: #ffffff;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
`;

const PopularBlogsTitle = styled.h3`
  font-size: 1.5rem;
  font-weight: bold;
  color: #333;
  margin-bottom: 15px;
`;

const BlogList = styled.ul`
  list-style: none;
  padding: 0;
  margin: 0;

  li {
    display: flex;
    align-items: center;
    margin-bottom: 10px;
    font-size: 1.1rem;
  }

  li:last-child {
    margin-bottom: 0;
  }

  .icon {
    margin-right: 10px;
    color: #007bff; /* Цвет иконки */
  }

  a {
    text-decoration: none;
    color: #007bff; /* Цвет ссылок */
    transition: color 0.3s ease;

    &:hover {
      color: #0056b3; /* Цвет ссылок при наведении */
    }
  }
`;

const Article = styled.article`
  background-color: #ffffff;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  margin-bottom: 20px;
`;

const MainLayout: React.FC = () => {
  return (
    <LayoutContainer>
      <MainContent>
        <Article>
          <h2>Простой способ развернуть локальный LLM</h2>
          <p>
            Большие языковые модели (LLM, Large Language Models) стали незаменимыми инструментами для разработчиков и исследователей...
          </p>
          {/* Остальное содержимое статьи */}
        </Article>
        {/* Можно добавить больше статей, как требуется */}
      </MainContent>
      <Sidebar>
        <PopularBlogsTitle>Популярные блоги</PopularBlogsTitle>
        <BlogList>
          <li>
            <FaBlog className="icon" /> <a href="#">RUVDS.com</a>
          </li>
          <li>
            <FaBlog className="icon" /> <a href="#">Selectel</a>
          </li>
          <li>
            <FaBlog className="icon" /> <a href="#">Timeweb Cloud</a>
          </li>
          <li>
            <FaBlog className="icon" /> <a href="#">МТС</a>
          </li>
          <li>
            <FaBlog className="icon" /> <a href="#">Сбер</a>
          </li>
          {/* Другие популярные блоги */}
        </BlogList>
      </Sidebar>
    </LayoutContainer>
  );
};

export default MainLayout;
