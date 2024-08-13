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
import 'chartjs-adapter-date-fns';
Chart.register(...registerables);

import { format } from 'date-fns';

export default {
    data() {
        return {
            graphData: {},
            recommendations: [],
            portfolioChart: null,
            diversificationChart: null,
            assets: [],
        };
    },
    mounted() {
        this.getGraphData();
        this.getAssets();

        const eventName = "update-analysis-page";
        this.emitter.on(eventName, (data) => {
            this.graphData = data.graphData;
            this.recommendations = data.recommendations;
            this.assets = data.assets.filter((row) => {
                return row.row_end === null;
            });

            this.createPortfolioChart();
            this.createDiversificationChart();
        });
    },
    methods: {
        getAssets() {
            const apiUrl = this.baseUrlForApiCall + 'assets';
            axios.get(apiUrl, {
                params: {
                    email: localStorage.getItem('email'),
                    token: localStorage.getItem('token')
                }
            }).then((response) => {
                this.assets = response.data.rows.filter((row) => {
                    return row.row_end === null;
                });

                if(this.assets.length > 0) {
                    this.createPortfolioChart();
                }
            });
        },
        getGraphData() {
            const apiUrl = this.baseUrlForApiCall + 'get_ig_analysis';
            axios.post(apiUrl, {
                email: localStorage.getItem('email'),
                token: localStorage.getItem('token')
            }).then((response) => {
                this.graphData = response.data.graph_data;
                this.recommendations = response.data.recommendations;

                if (this.graphData) {
                    //this.createPortfolioChart();
                    this.createDiversificationChart();
                }
            });
        },
        getGraphValue(key) {
            const graphValue = this.graphData.find(set => set.key === key);

            try {
                console.log(key, JSON.parse(graphValue.value));
                return JSON.parse(graphValue.value);
            } catch (error) {
                //return graphValue.value;
                return [];
            }
        },
        createPortfolioChart() {
            const ctx = document.getElementById('portfolio-chart').getContext('2d');

            // Destroy existing chart instance if it exists
            if (this.portfolioChart) {
                this.portfolioChart.destroy();
            }

            const dates = this.assets.map(asset => 
                format(new Date(asset.row_start), 'MMM d, yyyy HH:mm')
            );
            const values = this.assets.map(asset => asset.value);
            const assetNames = this.assets.map(asset => asset.asset);

            this.portfolioChart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: dates,
                    datasets: [{
                        label: 'Portfolio value',
                        data: values,
                        borderColor: 'rgb(75, 192, 192)',
                        tension: 0.1,
                        assetNames: assetNames
                    }]
                },
                options: {
                    scales: {
                        x: {
                            title: {
                                display: true,
                                text: 'Date'
                            }
                        },
                        y: {
                            beginAtZero: true,
                            title: {
                                display: true,
                                text: 'Asset Value'
                            }
                        }
                    },
                    plugins: {
                        tooltip: {
                            callbacks: {
                                label: (context) => {
                                    const index = context.dataIndex;
                                    const assetName = context.dataset.assetNames[index]; // Retrieve asset name using custom property
                                    const value = context.parsed.y;
                                    return `${assetName}: ${value}`;
                                }
                            }
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
                        //backgroundColor: ['rgb(75, 192, 192)', 'rgb(255, 99, 132)'],
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
