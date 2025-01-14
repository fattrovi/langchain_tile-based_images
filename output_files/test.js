以下是完整的 JavaScript 文件，根據你的需求：

```javascript
document.addEventListener('DOMContentLoaded', function() {
  // 確保正確引用 html2canvas
  if (typeof html2canvas === 'undefined') {
    console.error('html2canvas is not loaded. Please make sure to include html2canvas library.');
    return;
  }

  const captureBtn = document.getElementById('capture-btn');
  const bentoGrid = document.querySelector('.bento-grid');

  if (!captureBtn || !bentoGrid) {
    console.error('Required elements are not found in the document.');
    return;
  }

  captureBtn.addEventListener('click', function() {
    // 隱藏按鈕
    captureBtn.style.display = 'none';

    // 使用 html2canvas 截圖
    html2canvas(bentoGrid, { scale: 3 })
      .then(canvas => {
        // 將 canvas 轉換為圖片並下載
        const link = document.createElement('a');
        link.download = 'screenshot.png';
        link.href = canvas.toDataURL('image/png');
        link.click();

        // 恢復按鈕顯示
        captureBtn.style.display = 'inline-block';
      })
      .catch(error => {
        console.error('An error occurred during screenshot capture:', error);
        alert('截圖失敗，請稍後再試。');
        
        // 恢復按鈕顯示
        captureBtn.style.display = 'inline-block';
      });
  });
});
```

這段 JavaScript 代碼實現了以下功能：

1. 確保 `html2canvas` 庫已正確加載。
2. 確認必需的 DOM 元素（`.bento-grid` 和 `#capture-btn`）存在。
3. 為 `#capture-btn` 添加點擊事件監聽器。
4. 點擊按鈕後，隱藏按鈕，使用 `html2canvas` 對 `.bento-grid` 進行截圖，縮放比例設為 3 以提高解析度。
5. 成功截圖後，將圖片下載為 PNG 格式。
6. 無論成功或失敗，截圖完成後都恢復按鈕顯示，並在失敗時顯示錯誤提示。