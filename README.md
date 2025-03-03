# Multi-SpeedTest-Automation with OCR

This project automates the process of running speed tests on 5 different websites, taking screenshots, and extracting download speeds using easyOCR than exporting them to csv file.

## Table of Contents
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Usage](#usage)


## Features
- Supports multiple speed test websites: fast.com, openspeedtest.com, speed.measurementlab.net, speedsmart.net, and speedtest.net.
- Takes screenshots after completing the tests.
- Extracts download speed data based on specific keywords in OCR results.
- Saves the extracted text and download speed results in CSV format.
- Runs tests concurrently.

## Prerequisites
Ensure that the following are installed and set up on your system before running the script:

- **Python 3.x**: The script is written in Python.
- **Selenium WebDriver**: This script uses Selenium to interact with web pages.
- **Google Chrome**: The Chrome WebDriver (ChromeDriver) is required for Selenium to work with Chrome.
- **easyOCR**: The tool used to extract text from screenshots using Optical Character Recognition.

## Usage
- Open the speed test websites in a browser window.
- Perform the necessary actions to start the test (such as clicking buttons or waiting for results).
- Take screenshots after the test completes.
- Use easyOCR to extract text from the screenshots.
- Save the OCR results and download speeds into two separate CSV files which contains all the extracted OCR text for each test and the download speed results for each test.
