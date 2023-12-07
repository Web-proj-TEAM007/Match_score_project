import unittest
from unittest.mock import Mock, patch
from services import player_service
from data.models import PlayerStatistics
from common.exceptions import BadRequest

class PlayerService_Should(unittest.TestCase):

    def test_GetPlayerByID_returns_Successfully(self):

        with patch('services.player_service.read_query') as read_query, \
            patch('common.validators.form_ratio') as form_ratio_func:
            # Arrange
            read_query.return_value = [(1, 'Tarzan', 'Madagascar', 
                                        'BC Balkan', 1,0,1,1,1, 'Rocky', 
                                        'Dwayne','Asen')]
            form_ratio_func.return_value = '1/0'
            
            # Act
            expected = PlayerStatistics(id=1, full_name='Tarzan', country='Madagascar',
                                        sport_club='BC Balkan', matches_played=1,
                                        tournaments_played=1, tournaments_won=1,
                                        wl_ratio='1/0', most_played_against='Rocky',
                                        best_opponent='Dwayne', worst_opponent='Asen')
            res = player_service.get_player_by_id(1)

            # Assert
            self.assertEqual(expected.id, res.id)
            self.assertEqual(expected.full_name, res.full_name)
        
    def test_GetPlayerByID_returns_None(self):

        with patch('services.player_service.read_query') as read_query, \
            patch('common.validators.form_ratio') as form_ratio_func:
            # Arrange
            read_query.return_value = []
            form_ratio_func.return_value = []

            # Act
            res = player_service.get_player_by_id(1)

            self.assertIsNone(res)
    
    def test_PlayerExists_ID_returns_True(self):
        with patch('services.player_service.read_query') as read_query:

            read_query.return_value = '1'

            res = player_service.player_exists_id(1)

            self.assertTrue(res)
    
    def test_PlayerExists_ID_returns_False(self):
        with patch('services.player_service.read_query') as read_query:

            read_query.return_value = ''

            res = player_service.player_exists_id(1)

            self.assertFalse(res)
    
    def test_update_player_stat_matches_return_None(self):
        with patch('services.player_service.update_query') as update_query:

            update_query.return_value = 1
            res = player_service.update_player_stat_matches(1,True)

            self.assertIsNone(res)
    
    # def test_update_player_stat_matches_return_BadRequest(self):
    #     with patch('services.player_service.update_query') as update_query:

    #         update_query.return_value = 0
    #         res = player_service.update_player_stat_matches(1,True)

    #         self.assertRaises(BadRequest, res)


