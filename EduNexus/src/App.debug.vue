<template>
  <div>
    <h1>Hello World</h1>
    <p>This is a minimal Vue app</p>
    <div id="debug-info"></div>
  </div>
</template>

<script setup>
console.log('Debug: App component loaded')

// 创建调试信息
const debugDiv = document.getElementById('debug-info')
if (debugDiv) {
  debugDiv.innerHTML = `
    <p>Vue loaded successfully!</p>
    <p>Time: ${new Date().toLocaleString()}</p>
  `
}
</script>

<style>
body {
  margin: 0;
  padding: 20px;
  background-color: #f0f0f0;
}

h1 {
  color: #333;
}
</style>