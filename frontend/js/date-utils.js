/**
 * date-utils.js — 화면에 보여줄 "오늘 날짜"를 실제 현재 날짜 기준으로 반환
 *
 * 실시간처럼 보이게 하기 위해 실제 오늘 날짜로 표기함.
 */

function getTodayLabel() {
  const today = new Date();
  const yyyy = today.getFullYear();
  const mm = today.getMonth() + 1;
  const dd = today.getDate();
  return `${yyyy}년 ${mm}월 ${dd}일`;
}

function getTodayShortLabel() {
  const today = new Date();
  const mm = today.getMonth() + 1;
  const dd = today.getDate();
  return `${mm}월 ${dd}일`;
}