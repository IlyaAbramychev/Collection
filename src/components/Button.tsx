import styled from 'styled-components';

const Button = styled.button`
  background-color: #007bff;  /* Синий цвет фона */
  color: white;  /* Белый цвет текста */
  border: none;
  padding: 5px 15px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  
  &:hover {
    background-color: #0056b3;  /* Темно-синий при наведении */
  }
`;

export default Button;
