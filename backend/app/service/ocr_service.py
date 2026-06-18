# -*- coding: utf-8 -*-
"""
OCR 识别服务 / OCR Recognition Service
@Function: 提供验证码图片识别功能，支持多种图片预处理方式 / Provide captcha image recognition with multiple preprocessing methods
"""

import os
import cv2
import numpy as np
from typing import Optional, Tuple

from app.utils.logger import get_logger

logger = get_logger("ocr_service")


class OCRService:
    """OCR 识别服务类"""

    def __init__(self):
        """初始化 OCR 服务"""
        self._ocr = None
        self._initialized = False

    def _init_ocr(self):
        """延迟初始化 EasyOCR"""
        if self._initialized:
            return
        
        try:
            import easyocr
            
            self._ocr = easyocr.Reader(['en'], gpu=False)
            self._initialized = True
            logger.info("EasyOCR 初始化成功")
        except ImportError as e:
            logger.error(f"EasyOCR 未安装: {e}")
            raise RuntimeError("请安装 EasyOCR: pip install easyocr")
        except Exception as e:
            logger.error(f"EasyOCR 初始化失败: {e}")
            raise

    def preprocess_captcha(self, image_path: str) -> str:
        """预处理验证码图片
        
        Args:
            image_path: 原始验证码图片路径
            
        Returns:
            预处理后的图片路径
        """
        # 读取图片
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError(f"无法读取图片: {image_path}")
        
        # 转灰度
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # 二值化
        _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # 去噪
        denoised = cv2.medianBlur(binary, 3)
        
        # 膨胀（增强文字）
        kernel = np.ones((1, 1), np.uint8)
        dilated = cv2.dilate(denoised, kernel, iterations=1)
        
        # 保存预处理后的图片
        processed_path = image_path.replace('.png', '_processed.png')
        cv2.imwrite(processed_path, dilated)
        
        return processed_path

    def recognize(self, image_path: str, preprocess: bool = True) -> str:
        """识别验证码
        
        Args:
            image_path: 验证码图片路径
            preprocess: 是否预处理图片
            
        Returns:
            识别出的验证码文本
        """
        self._init_ocr()
        
        # 预处理图片
        if preprocess:
            processed_path = self.preprocess_captcha(image_path)
        else:
            processed_path = image_path
        
        try:
            # 使用 EasyOCR 识别
            result = self._ocr.readtext(processed_path)
            
            # 解析结果
            text = self._extract_text(result)
            
            # 清理文本（移除空格和特殊字符）
            text = self._clean_text(text)
            
            return text
            
        except Exception as e:
            logger.error(f"OCR 识别失败: {e}")
            raise

    def _extract_text(self, result) -> str:
        """从 OCR 结果中提取文本
        
        Args:
            result: EasyOCR 返回的结果
            
        Returns:
            提取的文本
        """
        texts = []
        
        # EasyOCR 返回格式: [(bbox, text, confidence), ...]
        if result:
            for item in result:
                if len(item) >= 2:
                    text = item[1]
                    texts.append(text)
        
        return ' '.join(texts)

    def _clean_text(self, text: str) -> str:
        """清理识别出的文本
        
        Args:
            text: 原始文本
            
        Returns:
            清理后的文本
        """
        import re
        
        # 移除空格
        text = text.replace(' ', '')
        
        # 只保留字母和数字
        text = re.sub(r'[^a-zA-Z0-9]', '', text)
        
        return text

    def recognize_with_retry(self, image_path: str, max_retries: int = 3, 
                            expected_length: int = 4) -> str:
        """带重试的验证码识别
        
        Args:
            image_path: 验证码图片路径
            max_retries: 最大重试次数
            expected_length: 期望的验证码长度
            
        Returns:
            识别出的验证码
        """
        for attempt in range(max_retries):
            try:
                # 尝试识别
                text = self.recognize(image_path, preprocess=(attempt > 0))
                
                # 检查长度是否符合预期
                if len(text) == expected_length:
                    logger.info(f"验证码识别成功 (尝试 {attempt + 1}): {text}")
                    return text
                
                logger.warning(f"验证码长度不符: {text} (尝试 {attempt + 1})")
                
            except Exception as e:
                logger.error(f"识别失败 (尝试 {attempt + 1}): {e}")
        
        # 所有重试都失败，返回最后一次的结果
        return text if 'text' in locals() else ""


# 全局单例
ocr_service = OCRService()
