document.addEventListener('DOMContentLoaded', () => {
    const analyzeBtn = document.getElementById('analyzeBtn');
    const userInput = document.getElementById('userInput');
    const result = document.getElementById('result');
    const legalIssues = document.getElementById('legalIssues');
    const relevantLaws = document.getElementById('relevantLaws');
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
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), 30000); // 30 seconds timeout

            const response = await fetch('/analyze', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ input }),
                signal: controller.signal
            });

            clearTimeout(timeoutId);

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || '分析失败。请重试。');
            }

            const data = await response.json();
            displayResult(data);
        } catch (error) {
            if (error.name === 'AbortError') {
                alert('分析超时。请尝试缩短输入文本或稍后重试。');
            } else {
                alert(error.message);
            }
        } finally {
            loading.classList.add('hidden');
        }
    });

    function displayResult(data) {
        legalIssues.innerHTML = `
            <h3 class="font-semibold mb-2">潜在法律问题：</h3>
            <ul class="list-disc pl-5">
                ${data.legal_issues.map(issue => `<li>${issue}</li>`).join('')}
            </ul>
        `;

        relevantLaws.innerHTML = `
            <h3 class="font-semibold mb-2">相关法律法规：</h3>
            <ul class="list-disc pl-5">
                ${data.relevant_laws.map(law => `<li>${law}</li>`).join('')}
            </ul>
        `;

        result.classList.remove('hidden');
    }
});
