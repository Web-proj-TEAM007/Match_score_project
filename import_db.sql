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
-- Table `matchscore_db`.`players_profiles`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `matchscore_db`.`players_profiles` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `full_name` TEXT(100) NOT NULL,
  `country` VARCHAR(45) NULL,
  `club` TEXT(50) NULL,
  PRIMARY KEY (`id`))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `matchscore_db`.`users`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `matchscore_db`.`users` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `email` TEXT(50) NOT NULL,
  `password` TEXT(20) NOT NULL,
  `player_profile_id` INT NULL,
  `user_role` VARCHAR(45) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `email_UNIQUE` (`email` ASC) VISIBLE,
  INDEX `fk_users_players_profiles_idx` (`player_profile_id` ASC) VISIBLE,
  CONSTRAINT `fk_users_players_profiles`
    FOREIGN KEY (`player_profile_id`)
    REFERENCES `matchscore_db`.`players_profiles` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `matchscore_db`.`players_statistics`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `matchscore_db`.`players_statistics` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `player_profile_id` INT NOT NULL,
  `matches_won` INT NOT NULL,
  `matches_lost` INT NOT NULL,
  `tournaments_won` INT NOT NULL,
  `tournaments_lost` INT NOT NULL,
  `tournaments_played` INT NOT NULL,
  `ratio` DECIMAL(2) NOT NULL,
  PRIMARY KEY (`id`),
  INDEX `fk_players_statistics_players_profiles1_idx` (`player_profile_id` ASC) VISIBLE,
  CONSTRAINT `fk_players_statistics_players_profiles1`
    FOREIGN KEY (`player_profile_id`)
    REFERENCES `matchscore_db`.`players_profiles` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `matchscore_db`.`tournaments`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `matchscore_db`.`tournaments` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `format` VARCHAR(45) NOT NULL,
  `title` VARCHAR(45) NOT NULL,
  `prize` INT NULL,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `title_UNIQUE` (`title` ASC) VISIBLE)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `matchscore_db`.`matches`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `matchscore_db`.`matches` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `format` VARCHAR(45) NOT NULL,
  `date` DATETIME NOT NULL,
  `tournament_id` INT NOT NULL,
  PRIMARY KEY (`id`),
  INDEX `fk_matches_tournaments1_idx` (`tournament_id` ASC) VISIBLE,
  CONSTRAINT `fk_matches_tournaments1`
    FOREIGN KEY (`tournament_id`)
    REFERENCES `matchscore_db`.`tournaments` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `matchscore_db`.`tournaments_has_players_profiles`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `matchscore_db`.`tournaments_has_players_profiles` (
  `tournament_id` INT NOT NULL,
  `player_profile_id` INT NOT NULL,
  PRIMARY KEY (`tournament_id`, `player_profile_id`),
  INDEX `fk_tournaments_has_players_profiles_players_profiles1_idx` (`player_profile_id` ASC) VISIBLE,
  INDEX `fk_tournaments_has_players_profiles_tournaments1_idx` (`tournament_id` ASC) VISIBLE,
  CONSTRAINT `fk_tournaments_has_players_profiles_tournaments1`
    FOREIGN KEY (`tournament_id`)
    REFERENCES `matchscore_db`.`tournaments` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_tournaments_has_players_profiles_players_profiles1`
    FOREIGN KEY (`player_profile_id`)
    REFERENCES `matchscore_db`.`players_profiles` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `matchscore_db`.`match_scores`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `matchscore_db`.`match_scores` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `matches_id` INT NOT NULL,
  `player_1_score` INT NOT NULL,
  `player_2_score` INT NOT NULL,
  `player_id_won` INT NOT NULL,
  PRIMARY KEY (`id`),
  INDEX `fk_score_matches1_idx` (`matches_id` ASC) VISIBLE,
  INDEX `fk_score_players_profiles1_idx` (`player_id_won` ASC) VISIBLE,
  CONSTRAINT `fk_score_matches1`
    FOREIGN KEY (`matches_id`)
    REFERENCES `matchscore_db`.`matches` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_score_players_profiles1`
    FOREIGN KEY (`player_id_won`)
    REFERENCES `matchscore_db`.`players_profiles` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `matchscore_db`.`matches_has_players_profiles`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `matchscore_db`.`matches_has_players_profiles` (
  `matches_id` INT NOT NULL,
  `player_profile_id` INT NOT NULL,
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
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `matchscore_db`.`requests`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `matchscore_db`.`requests` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `request` VARCHAR(45) NOT NULL,
  `user_id` INT NOT NULL,
  `player_profile_id` INT NOT NULL,
  PRIMARY KEY (`id`),
  INDEX `fk_requests_users1_idx` (`user_id` ASC) VISIBLE,
  INDEX `fk_requests_players_profiles1_idx` (`player_profile_id` ASC) VISIBLE,
  CONSTRAINT `fk_requests_users1`
    FOREIGN KEY (`user_id`)
    REFERENCES `matchscore_db`.`users` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_requests_players_profiles1`
    FOREIGN KEY (`player_profile_id`)
    REFERENCES `matchscore_db`.`players_profiles` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;