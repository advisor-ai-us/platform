<template>
    <div class="mental-health-page">
      <h2>Mental Health Advisor</h2>
      <el-card class="box-card" style="max-width: 700px;">
        <h3 style="margin-top: 0;">Phq9 graph:</h3>
        <canvas id="phq9-chart"></canvas>
      </el-card>
    </div>

    <ChatComponent :systemPrompt="systemPrompt" :pageName="pageName" />
</template>

<script>
import axios from 'axios';
import { Chart, registerables } from 'chart.js';
import 'chartjs-adapter-date-fns';
Chart.register(...registerables);

import ChatComponent from './ChatComponent.vue';
export default {
    data() {
        return {
            systemPrompt: '',
            pageName: 'mental-health-advisor',
            phq9Data: [],
            phq9Chart: null,
        };
    },
    components: {
        ChatComponent,
    },
    mounted() {
        this.mfToGetPhq9();

        // listen for the event to update the page
        const eventName = "update-mental-health-page";
        this.emitter.on(eventName, (data) => {
            this.phq9Data = data.phq9Data;
console.log('phq9Data:', this.phq9Data);
            if (this.phq9Data.length > 0) {
                console.log('phq9Data:', this.phq9Data);
                this.createPhq9Chart();
            }
        });
    },
    methods: {
        mfToGetPhq9() {
            const apiUrl = this.baseUrlForApiCall + 'get_phq9';
            axios.get(apiUrl, {
                params: {
                    email: localStorage.getItem('email'),
                    token: localStorage.getItem('token')
                }
            }).then((response) => {
                this.phq9Data = response.data;

                if (this.phq9Data.length > 0) {
                    this.createPhq9Chart();
                }
            });
        },
        createPhq9Chart() {
            // Step 1: Aggregate Scores by Date
            const aggregatedData = this.phq9Data.reduce((acc, row) => {
                const date = row.createdAt.split(' ')[0]; // Extract the date part
                if (!acc[date]) {
                    acc[date] = 0;
                }
                acc[date] += row.score;
                return acc;
            }, {});

            // Prepare data for the chart
            const labels = Object.keys(aggregatedData);
            const data = Object.values(aggregatedData);

            // Step 2: Use the Aggregated Data to Create the Chart
            const ctx = document.getElementById('phq9-chart').getContext('2d');

            if (this.phq9Chart) {
                this.phq9Chart.destroy();
            }

            this.phq9Chart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: labels,
                    datasets: [{
                        label: 'PHQ9 Score',
                        data: data,
                        borderColor: 'rgb(75, 192, 192)',
                        tension: 0.1
                    }]
                },
                options: {
                    scales: {
                        x: {
                            type: 'time',
                            time: {
                                unit: 'day',
                                displayFormats: {
                                    day: 'MMM d'
                                }
                            }
                        },
                        y: {
                            beginAtZero: true
                        }
                    }
                }
            });
        }
    }

};
</script>
  