<template>
    <div class="homepage-container">
        <header>
            <a href="/"><img src="/logo.png" alt="Advisor AI Logo"></a>
        </header>
        <div class="container">
            <h1 class="homepage-title">Connect with {{ keyword }}</h1>
        </div>
    </div>
</template>

<script>
export default {
    data() {
        return {
            keyword: ""
        };
    },
    mounted() {
        this.keyword = this.$route.params.keyword;
    }
};
</script>