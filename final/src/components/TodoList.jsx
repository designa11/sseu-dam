import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import notesIcon from "../../assets/notes.svg";
import moreIcon from "../../assets/more_horiz.svg";
import checkBoxChecked from "../../assets/check_box.svg";
import checkBoxUnchecked from "../../assets/check_box_outline_blank.svg";
import "./TodoList.css";

const TodoList = () => {
  const [tasks, setTasks] = useState([]);
  const navigate = useNavigate();

  // 서버에서 tasks 데이터를 가져옴
  useEffect(() => {
    fetch("http://localhost:3001/api/tasks")
      .then((response) => response.json())
      .then((data) => {
        // 데이터를 ID 기준으로 역순 정렬하여 가져옴
        const sortedTasks = data.sort((a, b) => b.id - a.id);
        // 최근 6개의 데이터만 가져오기
        setTasks(sortedTasks.slice(0, 6));
      })
      .catch((error) => console.error("Error fetching tasks:", error));
  }, []);

  // Task 완료 상태를 토글하는 함수
  const toggleTask = (id, completed) => {
    // 임시로 상태 업데이트
    const updatedTasks = tasks.map((task) =>
      task.id === id ? { ...task, completed: !completed } : task
    );
    setTasks(updatedTasks);

    // 서버에 업데이트 요청 보내기
    fetch(`http://localhost:3001/api/tasks/${id}/completed`, {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ completed: !completed }),
    })
      .then((response) => {
        if (!response.ok) {
          throw new Error("Network response was not ok");
        }
        return response.json();
      })
      .then((data) => {
        console.log("Task updated successfully:", data);
      })
      .catch((error) => {
        console.error("Error updating task:", error);
        setTasks(tasks); // 오류 발생 시 상태 롤백
      });
  };

  // 'more-options' 클릭 시 페이지 이동
  const goToAllTasks = () => {
    navigate("/all-tasks");
  };

  return (
    <div className="todo-list">
      <div className="todo-items">
        {/* Header 부분 */}
        <div className="todo-header">
          <div className="header-group">
            <img
              src={notesIcon}
              alt="오늘의 기록 아이콘"
              width="24"
              height="24"
              className="header-icon"
            />
            <h2>오늘의 기록</h2>
          </div>
          <div className="more-options" onClick={goToAllTasks}>
            <img
              src={moreIcon}
              alt="더보기 아이콘"
              width="24"
              height="24"
              style={{ cursor: "pointer" }}
            />
          </div>
        </div>

        {/* 할일 목록 */}
        <ul>
          {tasks.map((task) => (
            <li key={task.id} className={task.completed ? "completed" : ""}>
              <div
                className="checkbox-icon"
                onClick={() => toggleTask(task.id, task.completed)}
                style={{ cursor: "pointer" }}
              >
                <img
                  src={task.completed ? checkBoxChecked : checkBoxUnchecked}
                  alt={task.completed ? "Checked" : "Unchecked"}
                  width="24"
                  height="24"
                />
              </div>
              <span>{task.text}</span>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
};

export default TodoList;
