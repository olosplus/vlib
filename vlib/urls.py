# coding: utf-8
from django.conf.urls import patterns, url

urlpatterns = patterns('', url('savegrid/', 'vlib.views.save_grid'),)
urlpatterns += patterns('', url('deletegrid/', 'vlib.views.delete_grid'),)

