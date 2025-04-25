#!/usr/bin/env python3
"""
Graphical User Interface for NIKKE Automation Framework
"""

import os
import sys
import time
import threading
import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext, messagebox
from typing import Callable, Dict, Optional, List

# Import framework components
from src.utils.template_capture import capture_screenshot, interactive_region_select
from src.main import NikkeAutomation
from src.core.state.manager import GameState


class RedirectText:
    """Class to redirect stdout to a tkinter Text widget"""
    
    def __init__(self, text_widget: scrolledtext.ScrolledText):
        """
        Initialize with the target text widget.
        
        Args:
            text_widget: ScrolledText widget to redirect text to
        """
        self.text_widget = text_widget
        self.buffer = ""
    
    def write(self, string: str):
        """Write text to the text widget"""
        self.buffer += string
        self.text_widget.configure(state="normal")
        self.text_widget.insert(tk.END, string)
        self.text_widget.see(tk.END)
        self.text_widget.configure(state="disabled")
    
    def flush(self):
        """Flush the buffer"""
        self.text_widget.configure(state="normal")
        self.text_widget.insert(tk.END, self.buffer)
        self.buffer = ""
        self.text_widget.see(tk.END)
        self.text_widget.configure(state="disabled")


class NikkeAutomationGUI:
    """GUI for the NIKKE Automation Framework"""
    
    def __init__(self, root: tk.Tk):
        """
        Initialize the GUI.
        
        Args:
            root: Tkinter root window
        """
        self.root = root
        self.root.title("NIKKE Automation Framework")
        self.root.geometry("800x600")
        self.root.minsize(800, 600)
        
        # Create main tab control
        self.tab_control = ttk.Notebook(root)
        
        # Create tabs
        self.tab_capture = ttk.Frame(self.tab_control)
        self.tab_test = ttk.Frame(self.tab_control)
        self.tab_run = ttk.Frame(self.tab_control)
        
        # Add tabs to notebook
        self.tab_control.add(self.tab_capture, text="Template Capture")
        self.tab_control.add(self.tab_test, text="Test")
        self.tab_control.add(self.tab_run, text="Run Automation")
        
        # Pack the tab control
        self.tab_control.pack(expand=1, fill="both")
        
        # Initialize tabs
        self._init_capture_tab()
        self._init_test_tab()
        self._init_run_tab()
        
        # Create a common output area at the bottom
        self._init_output_area()
        
        # Set up stdout redirection
        self.stdout_redirect = RedirectText(self.output_text)
        self.original_stdout = sys.stdout
        
        # Keep track of all buttons for enabling/disabling
        self.buttons = []
        self._collect_buttons(self.root)
    
    def _collect_buttons(self, widget):
        """
        Recursively collect all buttons in the widget tree.
        
        Args:
            widget: The widget to start collection from
        """
        if isinstance(widget, ttk.Button):
            self.buttons.append(widget)
        
        # Recursively collect buttons from children
        try:
            children = widget.winfo_children()
            for child in children:
                self._collect_buttons(child)
        except (AttributeError, tk.TclError):
            pass
    
    def _init_capture_tab(self):
        """Initialize the Template Capture tab"""
        frame = ttk.Frame(self.tab_capture, padding=10)
        frame.pack(fill="both", expand=True)
        
        # Template name
        ttk.Label(frame, text="UI Element Name:").grid(row=0, column=0, sticky="w", pady=5)
        self.capture_name_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.capture_name_var).grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        
        # Category
        ttk.Label(frame, text="Category:").grid(row=1, column=0, sticky="w", pady=5)
        self.capture_category_var = tk.StringVar()
        category_combobox = ttk.Combobox(frame, textvariable=self.capture_category_var)
        category_combobox["values"] = ("home", "battle", "shop", "common")
        category_combobox.grid(row=1, column=1, sticky="ew", padx=5, pady=5)
        
        # Output directory
        ttk.Label(frame, text="Output Directory:").grid(row=2, column=0, sticky="w", pady=5)
        self.capture_output_var = tk.StringVar(value="resources/templates")
        output_entry = ttk.Entry(frame, textvariable=self.capture_output_var)
        output_entry.grid(row=2, column=1, sticky="ew", padx=5, pady=5)
        
        browse_button = ttk.Button(frame, text="Browse...", command=self._browse_output_dir)
        browse_button.grid(row=2, column=2, padx=5, pady=5)
        
        # Multiple captures
        ttk.Label(frame, text="Multiple Captures:").grid(row=3, column=0, sticky="w", pady=5)
        self.capture_multi_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(frame, variable=self.capture_multi_var).grid(row=3, column=1, sticky="w", padx=5, pady=5)
        
        # Count and interval (only shown when multiple captures is enabled)
        self.multi_frame = ttk.Frame(frame)
        self.multi_frame.grid(row=4, column=0, columnspan=3, sticky="ew", pady=5)
        
        ttk.Label(self.multi_frame, text="Count:").grid(row=0, column=0, sticky="w", pady=5, padx=5)
        self.capture_count_var = tk.IntVar(value=1)
        ttk.Spinbox(self.multi_frame, from_=1, to=100, textvariable=self.capture_count_var).grid(
            row=0, column=1, sticky="ew", padx=5, pady=5
        )
        
        ttk.Label(self.multi_frame, text="Interval (s):").grid(row=1, column=0, sticky="w", pady=5, padx=5)
        self.capture_interval_var = tk.DoubleVar(value=1.0)
        ttk.Spinbox(self.multi_frame, from_=0.1, to=60.0, increment=0.1, textvariable=self.capture_interval_var).grid(
            row=1, column=1, sticky="ew", padx=5, pady=5
        )
        
        # Update multi frame visibility when the checkbox changes
        self.capture_multi_var.trace_add("write", self._update_multi_frame_visibility)
        self._update_multi_frame_visibility()
        
        # Capture button
        capture_button = ttk.Button(frame, text="Capture Template", command=self._capture_template)
        capture_button.grid(row=5, column=0, columnspan=3, pady=20)
        
        # Make the template name entry expand with the window
        frame.columnconfigure(1, weight=1)
    
    def _init_test_tab(self):
        """Initialize the Test tab"""
        frame = ttk.Frame(self.tab_test, padding=10)
        frame.pack(fill="both", expand=True)
        
        # Config file
        ttk.Label(frame, text="Config File:").grid(row=0, column=0, sticky="w", pady=5)
        self.test_config_var = tk.StringVar(value="config.yaml")
        config_entry = ttk.Entry(frame, textvariable=self.test_config_var)
        config_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        
        browse_button = ttk.Button(frame, text="Browse...", command=lambda: self._browse_file(self.test_config_var))
        browse_button.grid(row=0, column=2, padx=5, pady=5)
        
        # Run test button
        test_button = ttk.Button(frame, text="Run Test", command=self._run_test)
        test_button.grid(row=1, column=0, columnspan=3, pady=20)
        
        # Make the config entry expand with the window
        frame.columnconfigure(1, weight=1)
    
    def _init_run_tab(self):
        """Initialize the Run Automation tab"""
        frame = ttk.Frame(self.tab_run, padding=10)
        frame.pack(fill="both", expand=True)
        
        # Config file
        ttk.Label(frame, text="Config File:").grid(row=0, column=0, sticky="w", pady=5)
        self.run_config_var = tk.StringVar(value="config.yaml")
        config_entry = ttk.Entry(frame, textvariable=self.run_config_var)
        config_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        
        browse_button = ttk.Button(frame, text="Browse...", command=lambda: self._browse_file(self.run_config_var))
        browse_button.grid(row=0, column=2, padx=5, pady=5)
        
        # Navigation target
        ttk.Label(frame, text="Navigate To:").grid(row=1, column=0, sticky="w", pady=5)
        self.run_navigate_var = tk.StringVar()
        
        # Get all possible states from the GameState enum
        state_values = [state.name for state in GameState]
        
        navigate_combobox = ttk.Combobox(frame, textvariable=self.run_navigate_var)
        navigate_combobox["values"] = state_values
        navigate_combobox.grid(row=1, column=1, sticky="ew", padx=5, pady=5)
        
        # Run button
        run_button = ttk.Button(frame, text="Run Automation", command=self._run_automation)
        run_button.grid(row=2, column=0, columnspan=3, pady=20)
        
        # Make the config entry expand with the window
        frame.columnconfigure(1, weight=1)
    
    def _init_output_area(self):
        """Initialize the output text area at the bottom of the window"""
        # Create a frame for the output area
        output_frame = ttk.LabelFrame(self.root, text="Output", padding=10)
        output_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Create scrolled text widget for output
        self.output_text = scrolledtext.ScrolledText(output_frame, wrap=tk.WORD, state="disabled")
        self.output_text.pack(fill="both", expand=True)
        
        # Add a clear button
        clear_button = ttk.Button(output_frame, text="Clear Output", command=self._clear_output)
        clear_button.pack(anchor="se", pady=5)
    
    def _clear_output(self):
        """Clear the output text area"""
        self.output_text.configure(state="normal")
        self.output_text.delete(1.0, tk.END)
        self.output_text.configure(state="disabled")
    
    def _browse_output_dir(self):
        """Browse for an output directory"""
        directory = filedialog.askdirectory(
            initialdir=self.capture_output_var.get(),
            title="Select Output Directory"
        )
        if directory:
            self.capture_output_var.set(directory)
    
    def _browse_file(self, var: tk.StringVar):
        """
        Browse for a file and set the result to the given StringVar.
        
        Args:
            var: StringVar to set the selected file path to
        """
        filename = filedialog.askopenfilename(
            initialdir=os.path.dirname(var.get()),
            title="Select File",
            filetypes=(("YAML files", "*.yaml *.yml"), ("All files", "*.*"))
        )
        if filename:
            var.set(filename)
    
    def _update_multi_frame_visibility(self, *args):
        """Update visibility of the multiple captures options based on the checkbox"""
        if self.capture_multi_var.get():
            for child in self.multi_frame.winfo_children():
                child.grid()
        else:
            for child in self.multi_frame.winfo_children():
                child.grid_remove()
    
    def _redirect_stdout(self):
        """Redirect stdout to the output text widget"""
        sys.stdout = self.stdout_redirect
    
    def _restore_stdout(self):
        """Restore stdout to its original value"""
        sys.stdout = self.original_stdout
    
    def _run_in_thread(self, func: Callable, *args, **kwargs):
        """
        Run a function in a separate thread.
        
        Args:
            func: Function to run
            *args: Positional arguments to pass to the function
            **kwargs: Keyword arguments to pass to the function
        """
        # Disable all buttons
        for button in self.buttons:
            button["state"] = "disabled"
        
        # Redirect stdout
        self._redirect_stdout()
        
        def thread_func():
            try:
                func(*args, **kwargs)
            except Exception as e:
                print(f"Error: {str(e)}")
            finally:
                # Restore stdout
                self.root.after(0, self._restore_stdout)
                
                # Re-enable all buttons
                self.root.after(0, self._enable_buttons)
        
        # Start the thread
        thread = threading.Thread(target=thread_func)
        thread.daemon = True
        thread.start()
    
    def _enable_buttons(self):
        """Re-enable all buttons"""
        for button in self.buttons:
            button["state"] = "normal"
        
        # Refresh the button list in case any new buttons were added
        self.buttons = []
        self._collect_buttons(self.root)
    
    def _capture_template(self):
        """Capture a template image"""
        # Validate inputs
        name = self.capture_name_var.get().strip()
        if not name:
            messagebox.showerror("Error", "Template name is required")
            return
        
        self._run_in_thread(self._do_capture_template)
    
    def _do_capture_template(self):
        """Perform template capture (runs in a separate thread)"""
        print("=== Template Capture Tool ===")
        
        # Get values from UI
        name = self.capture_name_var.get().strip()
        category = self.capture_category_var.get().strip()
        output_dir = self.capture_output_var.get().strip()
        multiple = self.capture_multi_var.get()
        count = self.capture_count_var.get()
        interval = self.capture_interval_var.get()
        
        # Create output directory
        output_dir = os.path.join(output_dir, category) if category else output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        if multiple and count > 1:
            print(f"Capturing {count} templates with interval {interval}s")
            for i in range(count):
                if i > 0:
                    print(f"Waiting {interval}s before next capture...")
                    time.sleep(interval)
                
                # For multiple captures, append index to name
                template_name = f"{name}_{i+1}" if name else None
                
                # Perform capture
                print(f"Selecting region for template: {template_name}")
                region = interactive_region_select()
                
                if region:
                    capture_screenshot(output_dir, template_name, region)
                else:
                    print("Selection canceled.")
                    break
        else:
            # Perform capture
            print(f"Selecting region for template: {name}")
            region = interactive_region_select()
            
            if region:
                capture_screenshot(output_dir, name, region)
            else:
                print("Selection canceled.")
        
        print("Template capture completed.")
    
    def _run_test(self):
        """Run a test of the framework"""
        self._run_in_thread(self._do_run_test)
    
    def _do_run_test(self):
        """Perform framework test (runs in a separate thread)"""
        print("=== NIKKE Automation Test ===")
        
        # Get values from UI
        config_path = self.test_config_var.get().strip()
        
        # Create automation instance
        automation = NikkeAutomation(config_path=config_path)
        
        # Run the test
        print("Running test sequence...")
        automation.run_test()
        
        print("Test completed. Check the logs for details.")
    
    def _run_automation(self):
        """Run automation"""
        self._run_in_thread(self._do_run_automation)
    
    def _do_run_automation(self):
        """Perform automation (runs in a separate thread)"""
        print("=== NIKKE Automation ===")
        
        # Get values from UI
        config_path = self.run_config_var.get().strip()
        navigate_to = self.run_navigate_var.get().strip()
        
        # Create automation instance
        automation = NikkeAutomation(config_path=config_path)
        
        # Update state
        state = automation.update_state()
        print(f"Current state: {state}")
        
        # If a target state is specified, navigate to it
        if navigate_to:
            try:
                target_state = GameState[navigate_to]
                print(f"Navigating to: {target_state}")
                result = automation.navigate_to(target_state)
                
                if result:
                    print(f"Successfully navigated to {target_state}")
                else:
                    print(f"Failed to navigate to {target_state}")
            except KeyError:
                print(f"Invalid state: {navigate_to}")
                print(f"Available states: {[s.name for s in GameState]}")
        
        print("Automation completed.")


def main():
    """Main entry point for the GUI"""
    root = tk.Tk()
    app = NikkeAutomationGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main() 