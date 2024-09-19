document.addEventListener('DOMContentLoaded', () => {
    const analyzeBtn = document.getElementById('analyzeBtn');
    const userInput = document.getElementById('userInput');
    const result = document.getElementById('result');
    const analysisContent = document.getElementById('analysisContent');
    const loading = document.getElementById('loading');

    analyzeBtn.addEventListener('click', async () => {
        const input = userInput.value.trim();
        if (!input) {
            alert('请输入您的情况描述。');
            return;
        }

        loading.classList.remove('hidden');
        result.classList.add('hidden');

        try {
            const response = await fetch('/analyze', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ input }),
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || '分析失败。请重试。');
            }

            const data = await response.json();
            displayResult(data);
        } catch (error) {
            alert(error.message);
        } finally {
            loading.classList.add('hidden');
        }
    });

    function displayResult(data) {
        let resultHTML = '';

        resultHTML += `<div class="mb-6">
            <h3 class="text-xl font-semibold mb-2">识别到的问题：</h3>
            <ul class="list-disc pl-5">
                ${data.identified_issues.map(issue => `<li class="mb-1">${issue}</li>`).join('')}
            </ul>
        </div>`;

        resultHTML += `<div class="mb-6">
            <h3 class="text-xl font-semibold mb-2">相关法规：</h3>
            <ul class="list-disc pl-5">
                ${data.relevant_regulations.map(reg => `<li class="mb-1">${reg}</li>`).join('')}
            </ul>
        </div>`;

        resultHTML += `<div class="mb-6">
            <h3 class="text-xl font-semibold mb-2">解释：</h3>
            <ul class="list-disc pl-5">
                ${data.explanations.map(exp => `<li class="mb-1">${exp}</li>`).join('')}
            </ul>
        </div>`;

        resultHTML += `<div class="mb-6">
            <h3 class="text-xl font-semibold mb-2">建议：</h3>
            <ul class="list-disc pl-5">
                ${data.recommendations.map(rec => `<li class="mb-1">${rec}</li>`).join('')}
            </ul>
        </div>`;

        analysisContent.innerHTML = resultHTML;
        result.classList.remove('hidden');
    }
});
