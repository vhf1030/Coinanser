from django.urls import path
from coinanser.views import market_views, atpu_views, monitoring_views, community_views,\
    question_views, answer_views, comment_views, vote_views
from coinanser.views import rawdata_views  # google chart 인자 전달 test
# # import * 은 파일 level의 함수를 인식함 / 디렉터리인 경우 __init__.py 안의 함수를 인식함


app_name = 'coinanser'

urlpatterns = [
    path('home/', market_views.market_data, name='market_data'),
    path('accountprice/', atpu_views.atpu_board, name='atpu_board'),
    path('monitoring/', monitoring_views.order_board, name='order_board'),
    path('community/', community_views.question_board, name='question_board'),
    path('test/', rawdata_views.select_test, name='select_test'),  # google chart 인자 전달 test
    path('community/<int:question_id>/', community_views.detail, name='detail'),
    path('question/create/', question_views.question_create, name='question_create'),
    path('question/modify/<int:question_id>/', question_views.question_modify, name='question_modify'),
    path('question/delete/<int:question_id>/', question_views.question_delete, name='question_delete'),
    path('answer/create/<int:question_id>/', answer_views.answer_create, name='answer_create'),
    path('answer/modify/<int:answer_id>/', answer_views.answer_modify, name='answer_modify'),
    path('answer/delete/<int:answer_id>/', answer_views.answer_delete, name='answer_delete'),
    path('comment/create/question/<int:question_id>/', comment_views.comment_create_question, name='comment_create_question'),
    path('comment/modify/question/<int:comment_id>/', comment_views.comment_modify_question, name='comment_modify_question'),
    path('comment/delete/question/<int:comment_id>/', comment_views.comment_delete_question, name='comment_delete_question'),
    path('comment/create/answer/<int:answer_id>/', comment_views.comment_create_answer, name='comment_create_answer'),
    path('comment/modify/answer/<int:comment_id>/', comment_views.comment_modify_answer, name='comment_modify_answer'),
    path('comment/delete/answer/<int:comment_id>/', comment_views.comment_delete_answer, name='comment_delete_answer'),
    path('vote/question/<int:question_id>/', vote_views.vote_question, name='vote_question'),
    path('vote/answer/<int:answer_id>/', vote_views.vote_answer, name='vote_answer'),
]

