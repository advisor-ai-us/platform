<template>
    <div class="homepage-container">
        <!-- <header>
            <a href="/"><img src="/logo.png" alt="Advisor AI Logo"></a>
        </header> -->
        <div class="container people-talk-page" v-if="checkingForPlugin">
            <h1>Connecting with {{ keyword }}</h1>
            <p>Please wait while we connect you with {{ keyword }}...</p>
        </div>
        <FullPageChatComponent v-else :advisorPersonalityName="keyword" />
    </div>
</template>

<script>
import axios from 'axios';
import FullPageChatComponent from './FullPageChatComponent.vue';
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
        FullPageChatComponent
    },
    mounted() {
        this.userEmail = localStorage.getItem('email');
        this.token = localStorage.getItem('token');
        if (!this.userEmail || !this.token) {
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
                } else {
                    // go to the login page
                    this.$router.push({ name: 'LoginPage' });
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
    margin: 50px auto;
}
.people-talk-page h1 {
    margin-top: 0;
}
.people-talk-page p {
    margin-bottom: 0;
}
</style>