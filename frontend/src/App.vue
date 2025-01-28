<template>
  <div id="app">
    <h1>Battlecard AI</h1>
    <battlecard-list />
  </div>
</template>

<script>
import BattlecardList from './components/BattlecardList.vue'

export default {
  name: 'App',
  components: {
    BattlecardList
  }
}
</script> 