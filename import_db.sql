-- MySQL Workbench Forward Engineering

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';

-- -----------------------------------------------------
-- Schema mydb
-- -----------------------------------------------------
-- -----------------------------------------------------
-- Schema matchscore_db
-- -----------------------------------------------------

-- -----------------------------------------------------
-- Schema matchscore_db
-- -----------------------------------------------------
CREATE SCHEMA IF NOT EXISTS `matchscore_db` DEFAULT CHARACTER SET latin1 ;
USE `matchscore_db` ;

-- -----------------------------------------------------
-- Table `matchscore_db`.`tournaments`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `matchscore_db`.`tournaments` (
  `id` INT(11) NOT NULL AUTO_INCREMENT,
  `format` VARCHAR(45) NOT NULL,
  `title` VARCHAR(45) NOT NULL,
  `prize` INT(11) NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `title_UNIQUE` (`title` ASC) VISIBLE)
ENGINE = InnoDB
DEFAULT CHARACTER SET = latin1;


-- -----------------------------------------------------
-- Table `matchscore_db`.`matches`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `matchscore_db`.`matches` (
  `id` INT(11) NOT NULL AUTO_INCREMENT,
  `format` VARCHAR(45) NOT NULL,
  `date` DATETIME NOT NULL,
  `tournament_id` INT(11) NOT NULL,
  PRIMARY KEY (`id`),
  INDEX `fk_matches_tournaments1_idx` (`tournament_id` ASC) VISIBLE,
  CONSTRAINT `fk_matches_tournaments1`
    FOREIGN KEY (`tournament_id`)
    REFERENCES `matchscore_db`.`tournaments` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB
DEFAULT CHARACTER SET = latin1;


-- -----------------------------------------------------
-- Table `matchscore_db`.`players_profiles`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `matchscore_db`.`players_profiles` (
  `id` INT(11) NOT NULL AUTO_INCREMENT,
  `full_name` TINYTEXT NOT NULL,
  `country` VARCHAR(45) NULL DEFAULT NULL,
  `club` TINYTEXT NULL DEFAULT NULL,
  PRIMARY KEY (`id`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = latin1;


-- -----------------------------------------------------
-- Table `matchscore_db`.`match_scores`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `matchscore_db`.`match_scores` (
  `id` INT(11) NOT NULL AUTO_INCREMENT,
  `matches_id` INT(11) NOT NULL,
  `player_1_score` INT(11) NOT NULL,
  `player_2_score` INT(11) NOT NULL,
  `players_profiles_id` INT(11) NOT NULL,
  PRIMARY KEY (`id`, `players_profiles_id`),
  INDEX `fk_score_matches1_idx` (`matches_id` ASC) VISIBLE,
  INDEX `fk_match_scores_players_profiles1_idx` (`players_profiles_id` ASC) VISIBLE,
  CONSTRAINT `fk_score_matches1`
    FOREIGN KEY (`matches_id`)
    REFERENCES `matchscore_db`.`matches` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_match_scores_players_profiles1`
    FOREIGN KEY (`players_profiles_id`)
    REFERENCES `matchscore_db`.`players_profiles` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB
DEFAULT CHARACTER SET = latin1;


-- -----------------------------------------------------
-- Table `matchscore_db`.`matches_has_players_profiles`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `matchscore_db`.`matches_has_players_profiles` (
  `matches_id` INT(11) NOT NULL,
  `player_profile_id` INT(11) NOT NULL,
  PRIMARY KEY (`matches_id`, `player_profile_id`),
  INDEX `fk_matches_has_players_profiles_players_profiles1_idx` (`player_profile_id` ASC) VISIBLE,
  INDEX `fk_matches_has_players_profiles_matches1_idx` (`matches_id` ASC) VISIBLE,
  CONSTRAINT `fk_matches_has_players_profiles_matches1`
    FOREIGN KEY (`matches_id`)
    REFERENCES `matchscore_db`.`matches` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_matches_has_players_profiles_players_profiles1`
    FOREIGN KEY (`player_profile_id`)
    REFERENCES `matchscore_db`.`players_profiles` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB
DEFAULT CHARACTER SET = latin1;


-- -----------------------------------------------------
-- Table `matchscore_db`.`players_statistics`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `matchscore_db`.`players_statistics` (
  `id` INT(11) NOT NULL AUTO_INCREMENT,
  `matches_won` INT(11) NULL DEFAULT 0,
  `matches_lost` INT(11) NULL DEFAULT 0,
  `tournaments_won` INT(11) NULL DEFAULT 0,
  `tournaments_lost` INT(11) NULL DEFAULT 0,
  `tournaments_played` INT(11) NULL DEFAULT 0,
  `ratio` DECIMAL(2,0) NULL DEFAULT 0,
  `players_profiles_id` INT(11) NOT NULL,
  PRIMARY KEY (`id`, `players_profiles_id`),
  INDEX `fk_players_statistics_players_profiles1_idx` (`players_profiles_id` ASC) VISIBLE,
  CONSTRAINT `fk_players_statistics_players_profiles1`
    FOREIGN KEY (`players_profiles_id`)
    REFERENCES `matchscore_db`.`players_profiles` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB
DEFAULT CHARACTER SET = latin1;


-- -----------------------------------------------------
-- Table `matchscore_db`.`users`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `matchscore_db`.`users` (
  `id` INT(11) NOT NULL AUTO_INCREMENT,
  `email` TINYTEXT NOT NULL,
  `password` TINYTEXT NOT NULL,
  `user_role` VARCHAR(45) NOT NULL,
  `players_profiles_id` INT(11) NOT NULL,
  PRIMARY KEY (`id`, `players_profiles_id`),
  UNIQUE INDEX `email_UNIQUE` USING HASH (`email`) VISIBLE,
  INDEX `fk_users_players_profiles1_idx` (`players_profiles_id` ASC) VISIBLE,
  CONSTRAINT `fk_users_players_profiles1`
    FOREIGN KEY (`players_profiles_id`)
    REFERENCES `matchscore_db`.`players_profiles` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB
DEFAULT CHARACTER SET = latin1;


-- -----------------------------------------------------
-- Table `matchscore_db`.`requests`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `matchscore_db`.`requests` (
  `id` INT(11) NOT NULL AUTO_INCREMENT,
  `request` VARCHAR(45) NOT NULL,
  `user_id` INT(11) NOT NULL,
  `players_profiles_id` INT(11) NOT NULL,
  PRIMARY KEY (`id`, `players_profiles_id`),
  INDEX `fk_requests_users1_idx` (`user_id` ASC) VISIBLE,
  INDEX `fk_requests_players_profiles1_idx` (`players_profiles_id` ASC) VISIBLE,
  CONSTRAINT `fk_requests_users1`
    FOREIGN KEY (`user_id`)
    REFERENCES `matchscore_db`.`users` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_requests_players_profiles1`
    FOREIGN KEY (`players_profiles_id`)
    REFERENCES `matchscore_db`.`players_profiles` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB
DEFAULT CHARACTER SET = latin1;


-- -----------------------------------------------------
-- Table `matchscore_db`.`tournaments_has_players_profiles`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `matchscore_db`.`tournaments_has_players_profiles` (
  `tournament_id` INT(11) NOT NULL,
  `player_profile_id` INT(11) NOT NULL,
  PRIMARY KEY (`tournament_id`, `player_profile_id`),
  INDEX `fk_tournaments_has_players_profiles_players_profiles1_idx` (`player_profile_id` ASC) VISIBLE,
  INDEX `fk_tournaments_has_players_profiles_tournaments1_idx` (`tournament_id` ASC) VISIBLE,
  CONSTRAINT `fk_tournaments_has_players_profiles_players_profiles1`
    FOREIGN KEY (`player_profile_id`)
    REFERENCES `matchscore_db`.`players_profiles` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_tournaments_has_players_profiles_tournaments1`
    FOREIGN KEY (`tournament_id`)
    REFERENCES `matchscore_db`.`tournaments` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB
DEFAULT CHARACTER SET = latin1;


SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;
