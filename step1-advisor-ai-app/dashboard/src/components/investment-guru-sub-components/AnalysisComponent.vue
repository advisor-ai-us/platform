<template>
    <div class="analysis-page">
        <el-row>
            <el-col :span="12" style="padding-right: 15px;">
                <el-card>
                    <h3>Your Portfolio:</h3>
                    <canvas id="portfolio-chart"></canvas>
                </el-card>
            </el-col>
            <el-col :span="12" style="padding-left: 15px;">
                <el-card>
                    <h3>Your Diversification:</h3>
                    <canvas id="diversification-chart" style="width: 200px; height: 200px;"></canvas>
                </el-card>
            </el-col>
        </el-row>

        <el-row style="margin-top: 30px;">
            <el-col :span="24">
                <el-card>
                    <h3>Top 3 recommendations:</h3>
                    <ol>
                        <li v-for="(recommendation, index) in recommendations" :key="index">
                            <p>{{ recommendation }}</p>
                        </li>
                    </ol>
                </el-card>
            </el-col>
        </el-row>
    </div>
</template>

<script>
import axios from 'axios';
import { Chart, registerables } from 'chart.js';
Chart.register(...registerables);

export default {
    data() {
        return {
            graphData: {},
            recommendations: [],
            portfolioChart: null,
            diversificationChart: null,
        };
    },
    mounted() {
        this.getGraphData();

        const eventName = "update-analysis-page";
        this.emitter.on(eventName, (data) => {
            this.graphData = data.graphData;
            this.recommendations = data.recommendations;

            this.createPortfolioChart();
            this.createDiversificationChart();
        });
    },
    methods: {
        getGraphData() {
            const apiUrl = this.baseUrlForApiCall + 'get_ig_analysis';
            axios.post(apiUrl, {
                email: localStorage.getItem('email'),
                token: localStorage.getItem('token')
            }).then((response) => {
                this.graphData = response.data.graph_data;
                this.recommendations = response.data.recommendations;

                if (this.graphData) {
                    this.createPortfolioChart();
                    this.createDiversificationChart();
                }
            });
        },
        getGraphValue(key) {
            const graphValue = this.graphData.find(set => set.key === key);

            try {
                return JSON.parse(graphValue.value);
            } catch (error) {
                return graphValue.value;
            }
        },
        createPortfolioChart() {
            const ctx = document.getElementById('portfolio-chart').getContext('2d');

            // Destroy existing chart instance if it exists
            if (this.portfolioChart) {
                this.portfolioChart.destroy();
            }

            this.portfolioChart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: this.getGraphValue('line_chart_labels'),
                    datasets: [{
                        label: 'Portfolio value',
                        data: this.getGraphValue('line_chart_values'),
                        borderColor: 'rgb(75, 192, 192)',
                        tension: 0.1
                    }]
                },
                options: {
                    scales: {
                        y: {
                            beginAtZero: true
                        }
                    }
                }
            });
        },
        createDiversificationChart() {
            const ctx = document.getElementById('diversification-chart').getContext('2d');

            // Destroy existing chart instance if it exists
            if (this.diversificationChart) {
                this.diversificationChart.destroy();
            }

            this.diversificationChart = new Chart(ctx, {
                type: 'pie',
                data: {
                    labels: this.getGraphValue('pie_chart_labels'),
                    datasets: [{
                        label: 'Diversification',
                        data: this.getGraphValue('pie_chart_data'),
                        backgroundColor: ['rgb(75, 192, 192)', 'rgb(255, 99, 132)'],
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: {
                            position: 'top',
                        },
                        tooltip: {
                            callbacks: {
                                label: function(tooltipItem) {
                                    return tooltipItem.label + ': ' + tooltipItem.raw + '%';
                                }
                            }
                        }
                    }
                }
            });
        }
    }
};
</script>

<style>
canvas#diversification-chart {
    max-height: 330px;
}
</style>
