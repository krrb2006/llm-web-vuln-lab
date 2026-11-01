// 演示用：DOM XSS + 硬编码密钥
const API_KEY = "sk-demo-1234567890abcdef1234567890";
const params = new URLSearchParams(location.search);
document.getElementById("result").innerHTML = "搜索：" + params.get("q");
