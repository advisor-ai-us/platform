<template>
    <div class="homepage-container">
        <header>
            <a href="/"><img src="/logo.png" alt="Advisor AI Logo"></a>
        </header>
        <div class="container people-talk-page">
            <h1 v-if="checkingForPlugin">Connecting with {{ keyword }}</h1>
            <h1 v-else>Connected with {{ keyword }}</h1>
            <p v-if="checkingForPlugin">Please wait while we connect you with {{ keyword }}...</p>
            <p v-else>You are now connected to {{ keyword }}. Feel free to start chatting with him!.</p>
        </div>
        <ChatComponent v-if="!checkingForPlugin" :systemPrompt="systemPrompt" :advisorPersonalityName="keyword" />
    </div>
</template>

<script>
import axios from 'axios';
import ChatComponent from './ChatComponent.vue';
export default {
    data() {
        return {
            keyword: "",
            userEmail: "",
            token: '',
            checkingForPlugin: true,
            systemPrompt: '',
        };
    },
    components: {
        ChatComponent
    },
    mounted() {
        this.userEmail = localStorage.getItem('email');
        this.token = localStorage.getItem('token');
        if (!this.userEmail) {
            this.$router.push({ name: 'LoginPage' });
        }   

        this.keyword = this.$route.params.keyword;

        this.mfToCheckPlugin();
    },
    methods: {
        mfToCheckPlugin() {
            const url = this.baseUrlForApiCall + 'check_plugin';
            axios.post(url, {
                email: this.userEmail,
                token: this.token,
                plugin: this.keyword
            }).then((response) => {
                if(response.data.exists) {
                    this.checkingForPlugin = false;
                }
            }).catch((error) => {
                console.log(error);
            });
        }
    }
};
</script>

<style>
.people-talk-page {
    text-align: center;
}
.people-talk-page h1 {
    margin-top: 0;
}
.people-talk-page p {
    margin-bottom: 0;
}
</style>