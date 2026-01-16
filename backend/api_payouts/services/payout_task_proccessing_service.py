import logging
from datetime import timedelta
from django.utils import timezone
from django.db import transaction
from django.shortcuts import get_object_or_404


from ..models import Payout

logger = logging.getLogger(__name__)


class PayoutProcessingService:
    """Сервис для обработки выплат"""

    def __init__(self, payout_id, task=None):
        self.payout_id = payout_id
        self.payout = None
        self.result = {}
        self.task = task

    def process(self):
        """
        Основной метод обработки выплаты
        Возвращает результат выполнения
        """
        try:
            self._setup()
            self._validate()
            self._set_processing()
            self._simulate_processing()
            self._complete()
            return self._success_result()

        except Payout.DoesNotExist:
            return self._not_found_result()
        except Exception as exc:
            return self._handle_error(exc)

    def _setup(self):
        """Этап 1: Получение объекта выплаты"""
        logger.info(f"Начинаю обработку выплаты с ID: {self.payout_id}")
        self.payout = get_object_or_404(Payout, id=self.payout_id)

        # Обновляем прогресс задачи если есть task
        if self.task:
            self.task.update_state(
                state='PROGRESS',
                meta={'current': 1, 'total': 5, 'stage': 'setup'}
            )

    def _validate(self):
        """Этап 2: Валидация и проверка идемпотентности"""
        if self.payout.status == 'completed':
            logger.info(f"Выплата {self.payout_id} уже выполнена ранее")
            self.result = {'already_completed': True}
            raise StopProcessing()

        elif self.payout.status == 'processing':
            self._check_stuck_processing()

        # Обновляем прогресс
        if self.task:
            self.task.update_state(
                state='PROGRESS',
                meta={'current': 2, 'total': 5, 'stage': 'validation'}
            )

    def _check_stuck_processing(self):
        """Проверка зависшей обработки"""
        if self.payout.updated_at < timezone.now() - timedelta(minutes=5):
            logger.warning(f"Выплата {self.payout_id} зависла в processing")
            # Сброс статуса для повторной обработки
            with transaction.atomic():
                self.payout.status = 'pending'
                self.payout.save(update_fields=['status', 'updated_at'])
        else:
            raise ProcessingInProgress()

    def _set_processing(self):
        """Этап 3: Установка статуса 'в обработке'"""
        with transaction.atomic():
            self.payout.status = 'processing'
            self.payout.save(update_fields=['status', 'updated_at'])
        logger.info(f"Выплата {self.payout_id} переведена в статус 'processing'")

        # Обновляем прогресс
        if self.task:
            self.task.update_state(
                state='PROGRESS',
                meta={'current': 3, 'total': 5, 'stage': 'processing'}
            )

    def _simulate_processing(self):
        """Улучшенная имитация обработки"""
        logger.info(f"Имитация обработки выплаты {self.payout_id}...")

        stages = [
            {"name": "Проверка данных", "duration": 0.5},
            {"name": "Верификация баланса", "duration": 0.5},
            {"name": "Резервирование средств", "duration": 0.5},
            {"name": "Подготовка транзакции", "duration": 0.5},
            {"name": "Отправка в платежную систему", "duration": 0.5}
        ]

        for stage in stages:
            logger.info(f"Этап '{stage['name']}' для выплаты {self.payout_id}")

            if self.task:
                 self.task.update_state(
                    state='PROGRESS',
                    meta={
                        'payout_id': str(self.payout_id),
                        'stage': stage['name'],
                        'progress': f"Выполняется {stage['name']}"
                    }
                )
        logger.info(f"Имитация обработки завершена для выплаты {self.payout_id}")

    def _complete(self):
        """Этап 5: Завершение обработки"""
        logger.info(f"Завершение обработки выплаты {self.payout_id}")
        with transaction.atomic():
            self.payout.status = 'completed'
            self.payout.save(update_fields=['status', 'updated_at'])
        logger.info(f"Выплата {self.payout_id} успешно обработана")

        # Обновляем прогресс
        if self.task:
            self.task.update_state(
                state='PROGRESS',
                meta={'current': 5, 'total': 5, 'stage': 'completion'}
            )

    def _success_result(self):
        """Формирование успешного результата"""
        return {
            'success': True,
            'payout_id': self.payout_id,
            'status': 'completed',
            'message': 'Выплата успешно обработана',
            'completed_at': self.payout.updated_at.isoformat()
        }

    def _not_found_result(self):
        """Обработка случая, когда выплата не найдена"""
        logger.error(f"Выплата с ID {self.payout_id} не найдена")
        return {
            'success': False,
            'payout_id': self.payout_id,
            'error': 'Выплата не найдена'
        }

    def _handle_error(self, exc):
        """Обработка ошибок"""
        logger.error(f"Критическая ошибка при обработке выплаты {self.payout_id}: {str(exc)}")

        if isinstance(exc, (StopProcessing, ProcessingInProgress)):
            # Эти исключения не требуют смены статуса на failed
            if hasattr(exc, 'result'):
                logger.error(exc.result)
                return exc.result
            raise exc

        # Обновление статуса на "ошибка"
        self._mark_as_failed(exc)
        raise exc

    def _mark_as_failed(self, error):
        """Обновление статуса выплаты на 'failed'"""
        try:
            with transaction.atomic():
                payout = Payout.objects.get(id=self.payout_id)
                payout.status = 'failed'
                if payout.description:
                    payout.description += f'\nОшибка: {str(error)}'
                else:
                    payout.description = f'Ошибка: {str(error)}'
                payout.save(update_fields=['status', 'description', 'updated_at'])
        except Exception as update_exc:
            logger.error(f"Не удалось обновить статус для {self.payout_id}: {str(update_exc)}")


class StopProcessing(Exception):
    """Исключение для остановки обработки (например, уже выполнена)"""

    def __init__(self, result=None):
        self.result = result
        super().__init__()


class ProcessingInProgress(Exception):
    """Исключение для обработки, которая уже выполняется"""
    pass