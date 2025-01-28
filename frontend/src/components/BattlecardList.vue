<template>
  <div>
    <h2>All Battlecards</h2>
    <ul>
      <li v-for="(card, index) in battlecards" :key="index">
        {{ card }}
      </li>
    </ul>
    <button @click="generateBattlecard">Auto-Generate Battlecard</button>
  </div>
</template>

<script>
export default {
  name: 'BattlecardList',
  data() {
    return {
      battlecards: []
    }
  },
  mounted() {
    this.fetchBattlecards()
  },
  methods: {
    fetchBattlecards() {
      fetch('/api/battlecards')
        .then(res => res.json())
        .then(data => {
          this.battlecards = data.battlecards
        })
        .catch(err => console.error(err))
    },
    generateBattlecard() {
      fetch('/api/battlecards/auto-generate', { method: 'POST' })
        .then(res => res.json())
        .then(data => {
          alert('Battlecard generated!')
          console.log(data)
          this.fetchBattlecards()
        })
        .catch(err => console.error(err))
    }
  }
}
</script> 