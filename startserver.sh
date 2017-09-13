#!/bin/sh
# Start Backend Server

gunicorn application:application -b localhost:8000 
