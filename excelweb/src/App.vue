<script setup>
import { RouterLink, RouterView } from 'vue-router'
import HelloWorld from './components/HelloWorld.vue'
import Upload from './components/upload.vue';
</script>

<template>
  <!-- <div><h1>123</h1></div> -->
   <div>
    <router-view></router-view>
   </div>
  
  
 
</template>

<style>
/* 全局样式 */
/* body {
  margin: 0;
  font-family: sans-serif;
} */
</style>
