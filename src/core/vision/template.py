import cv2
import numpy as np
import os
from typing import Tuple, List, Dict, Optional, Union, Literal
from enum import Enum
import logging


class MatchMethod(Enum):
    """Enum for different template matching methods."""
    EXACT = cv2.TM_CCOEFF_NORMED
    SQDIFF = cv2.TM_SQDIFF_NORMED
    CCORR = cv2.TM_CCORR_NORMED


class TemplateMatch:
    """Represents the result of a template match."""
    
    def __init__(self, 
                 top_left: Tuple[int, int], 
                 bottom_right: Tuple[int, int],
                 confidence: float, 
                 template_name: str,
                 method: MatchMethod):
        """
        Initialize a template match result.
        
        Args:
            top_left: (x, y) coordinates of the top-left corner of the match
            bottom_right: (x, y) coordinates of the bottom-right corner of the match
            confidence: confidence score (0.0 to 1.0)
            template_name: name of the matched template
            method: method used for matching
        """
        self.top_left = top_left
        self.bottom_right = bottom_right
        self.confidence = confidence
        self.template_name = template_name
        self.method = method
        
    @property
    def center(self) -> Tuple[int, int]:
        """Get the center coordinates of the match."""
        center_x = (self.top_left[0] + self.bottom_right[0]) // 2
        center_y = (self.top_left[1] + self.bottom_right[1]) // 2
        return (center_x, center_y)
    
    @property
    def width(self) -> int:
        """Get the width of the match."""
        return self.bottom_right[0] - self.top_left[0]
    
    @property
    def height(self) -> int:
        """Get the height of the match."""
        return self.bottom_right[1] - self.top_left[1]


class TemplateMatcher:
    """
    Template matching engine for the NIKKE Automation Framework.
    Supports multiple matching methods and confidence thresholds.
    """
    
    def __init__(self, templates_dir: str = None):
        """
        Initialize the template matcher.
        
        Args:
            templates_dir: Directory containing template images.
                          If None, no templates are loaded initially.
        """
        self.templates: Dict[str, np.ndarray] = {}
        self.logger = logging.getLogger(__name__)
        
        if templates_dir and os.path.isdir(templates_dir):
            self.load_templates_from_directory(templates_dir)
    
    def load_template(self, path: str, name: Optional[str] = None) -> bool:
        """
        Load a template image from a file.
        
        Args:
            path: Path to the template image
            name: Name to assign to the template. If None, uses the filename without extension.
            
        Returns:
            bool: True if the template was loaded successfully, False otherwise.
        """
        if not os.path.isfile(path):
            self.logger.error(f"Template file not found: {path}")
            return False
        
        try:
            # Load the image and convert to BGR for consistency
            template = cv2.imread(path)
            
            if template is None:
                self.logger.error(f"Failed to load template image: {path}")
                return False
            
            # Use filename as template name if not provided
            if name is None:
                name = os.path.splitext(os.path.basename(path))[0]
            
            self.templates[name] = template
            self.logger.info(f"Loaded template '{name}' from {path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error loading template {path}: {str(e)}")
            return False
    
    def load_templates_from_directory(self, directory: str, 
                                     extensions: List[str] = None) -> int:
        """
        Load all template images from a directory.
        
        Args:
            directory: Directory containing template images
            extensions: List of file extensions to load (e.g., ['.png', '.jpg']). 
                       If None, loads all common image extensions.
                       
        Returns:
            int: Number of templates loaded successfully
        """
        if extensions is None:
            extensions = ['.png', '.jpg', '.jpeg', '.bmp']
        
        count = 0
        
        if not os.path.isdir(directory):
            self.logger.error(f"Template directory not found: {directory}")
            return count
        
        for root, _, files in os.walk(directory):
            for file in files:
                if any(file.lower().endswith(ext) for ext in extensions):
                    path = os.path.join(root, file)
                    # The template name will include the subdirectory structure
                    rel_path = os.path.relpath(path, directory)
                    name = os.path.splitext(rel_path)[0].replace(os.path.sep, '/')
                    if self.load_template(path, name):
                        count += 1
        
        self.logger.info(f"Loaded {count} templates from {directory}")
        return count
    
    def find_template(self, image: np.ndarray, template_name: str,
                      method: MatchMethod = MatchMethod.EXACT,
                      threshold: float = 0.8,
                      multiple: bool = False,
                      max_results: int = 5) -> Union[Optional[TemplateMatch], List[TemplateMatch]]:
        """
        Find a template in the image.
        
        Args:
            image: Image to search in
            template_name: Name of the template to find
            method: Matching method to use
            threshold: Confidence threshold (0.0 to 1.0)
            multiple: If True, returns all matches above threshold. If False, returns best match.
            max_results: Maximum number of results to return when multiple=True
            
        Returns:
            If multiple=False: TemplateMatch object for the best match, or None if no match found.
            If multiple=True: List of TemplateMatch objects for all matches above threshold.
        """
        if template_name not in self.templates:
            self.logger.error(f"Template '{template_name}' not found")
            return [] if multiple else None
        
        template = self.templates[template_name]
        
        # Check if template is larger than the image
        if template.shape[0] > image.shape[0] or template.shape[1] > image.shape[1]:
            self.logger.warning(f"Template '{template_name}' is larger than the image")
            return [] if multiple else None
        
        # Apply template matching
        result = cv2.matchTemplate(image, template, method.value)
        
        # For SQDIFF methods, good matches are minimum values
        # For correlation methods, good matches are maximum values
        invert_score = (method == MatchMethod.SQDIFF)
        
        if multiple:
            matches = []
            while len(matches) < max_results:
                # Find the best match location
                min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
                
                # Calculate score based on the method
                score = 1 - min_val if invert_score else max_val
                loc = min_loc if invert_score else max_loc
                
                # If score is below threshold, break
                if score < threshold:
                    break
                
                # Create template match object
                h, w = template.shape[:2]
                match = TemplateMatch(
                    top_left=loc,
                    bottom_right=(loc[0] + w, loc[1] + h),
                    confidence=score,
                    template_name=template_name,
                    method=method
                )
                matches.append(match)
                
                # Mask out the found location to find the next best match
                mask_size = 5  # Larger mask to avoid overlapping matches
                cv2.rectangle(
                    result, 
                    (max(0, loc[0] - mask_size), max(0, loc[1] - mask_size)),
                    (min(result.shape[1], loc[0] + w + mask_size), min(result.shape[0], loc[1] + h + mask_size)),
                    0, 
                    -1
                )
            
            return matches
        else:
            # Find the best match location
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
            
            # Calculate score based on the method
            score = 1 - min_val if invert_score else max_val
            loc = min_loc if invert_score else max_loc
            
            # If score is below threshold, return None
            if score < threshold:
                return None
            
            # Create template match object
            h, w = template.shape[:2]
            return TemplateMatch(
                top_left=loc,
                bottom_right=(loc[0] + w, loc[1] + h),
                confidence=score,
                template_name=template_name,
                method=method
            )
    
    def find_all_templates(self, image: np.ndarray, 
                          method: MatchMethod = MatchMethod.EXACT,
                          threshold: float = 0.8,
                          max_results_per_template: int = 3) -> Dict[str, List[TemplateMatch]]:
        """
        Find all loaded templates in the image.
        
        Args:
            image: Image to search in
            method: Matching method to use
            threshold: Confidence threshold (0.0 to 1.0)
            max_results_per_template: Maximum number of results to return per template
            
        Returns:
            Dict mapping template names to lists of TemplateMatch objects
        """
        results = {}
        
        for template_name in self.templates:
            matches = self.find_template(
                image, 
                template_name, 
                method=method, 
                threshold=threshold, 
                multiple=True,
                max_results=max_results_per_template
            )
            
            if matches:
                results[template_name] = matches
        
        return results
