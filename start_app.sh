#!/bin/bash

gunicorn app:app -b localhost:8080
